<template>
  <div class="questionnaire-container">
    <el-card class="questionnaire-card enhanced-card fade-in">
      <template #header>
        <div class="card-header">
          <h3>Questionnaire</h3>
          <p class="subtitle">Please answer the following questions, and we will provide personalized investment advice for you.</p>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="submitted" class="submitted-container">
        <el-result
          icon="success"
          title="Questionnaire submitted successfully!"
          sub-title="Thank you for your participation, we will provide personalized investment advice for you based on your answers."
        >
          <template #extra>
            <el-button type="primary" class="round-btn gradient-btn" @click="resetQuestionnaire">Re-fill</el-button>
            <el-button class="round-btn info-btn" @click="viewResponses">View my answers</el-button>
          </template>
        </el-result>
        <div v-if="aiLoading" class="ai-suggestion-block" style="text-align:center;">
          <el-icon class="is-loading" style="font-size:28px;margin-bottom:8px;"/>
          <div>AI suggestions generating...</div>
        </div>
        <div v-else>
          <div v-if="aiStockSuggestion" class="ai-suggestion-block">
            <h4>AI stock/asset suggestions</h4>
            <div style="margin-bottom: 8px;">
              <el-tag v-for="ticker in aiStockSuggestion.tickers" :key="ticker" type="info" style="margin-right: 4px;">{{ ticker }}</el-tag>
            </div>
            <p style="color: #888;">{{ aiStockSuggestion.explanation }}</p>
          </div>
          <div v-if="aiMetricSuggestion" class="ai-suggestion-block">
            <h4>AI metric suggestions</h4>
            <el-tag type="success">{{ aiMetricSuggestion.recommended_metric }}</el-tag>
            <p style="color: #888;">{{ aiMetricSuggestion.explanation }}</p>
          </div>
        </div>

        <!-- Create Portfolio button and modal -->
        <div class="portfolio-btn-group">
          <el-button
            v-if="aiStockSuggestion && aiStockSuggestion.tickers && aiStockSuggestion.tickers.length"
            type="primary"
            class="round-btn gradient-btn"
            @click="showCreatePortfolioModal = true"
          >
            Create Portfolio
          </el-button>
          <el-button
            v-if="portfolioCreated"
            type="success"
            class="round-btn gradient-btn"
            @click="showOptimizeModal = true"
          >
            Optimize Portfolio
          </el-button>
        </div>

        <el-dialog
          v-model="showCreatePortfolioModal"
          title="Create Portfolio"
          width="800px"
          :close-on-click-modal="false"
          class="enhanced-dialog create-portfolio-dialog"
        >
          <el-form :model="newPortfolio" :rules="portfolioRules" ref="portfolioFormRef" label-width="120px" class="create-portfolio-form">
            <el-form-item label="Portfolio Name" prop="name">
              <el-input v-model="newPortfolio.name" placeholder="Please enter portfolio name" />
            </el-form-item>
            <el-form-item label="Start Date" prop="start_date">
              <el-date-picker v-model="newPortfolio.start_date" type="date" placeholder="Please select start date" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Stock and Weight">
              <div class="portfolio-row-list">
                <div v-for="(item, idx) in newPortfolio.items" :key="idx" class="portfolio-row">
                  <el-select
                    v-model="item.ticker"
                    placeholder="Please select stock"
                    style="width: 180px"
                    :disabled="false"
                    filterable
                  >
                    <el-option
                      v-for="ticker in aiStockSuggestion.tickers"
                      :key="ticker"
                      :label="ticker"
                      :value="ticker"
                      :disabled="isTickerSelected(ticker, idx)"
                    />
                  </el-select>
                  <el-input-number
                    v-model="item.weight"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    :precision="2"
                    placeholder="Weight"
                    style="width: 120px"
                  />
                  <el-button
                    type="danger"
                    class="round-btn remove-btn delete-btn"
                    @click="removeTicker(idx)"
                    :disabled="newPortfolio.items.length === 1"
                  >Delete</el-button>
                </div>
              </div>
            </el-form-item>
          </el-form>
          <template #footer>
            <div class="dialog-footer-btns">
              <el-button
                type="primary"
                class="round-btn gradient-btn add-btn"
                @click="addTicker"
                :disabled="newPortfolio.items.length >= aiStockSuggestion.tickers.length"
              >Add Stock</el-button>
              <el-button class="round-btn info-btn" @click="showCreatePortfolioModal = false">Cancel</el-button>
              <el-button type="primary" class="round-btn gradient-btn" :loading="creatingPortfolio" @click="submitPortfolio">Create</el-button>
            </div>
          </template>
        </el-dialog>

        <!-- Optimize button and modal -->
        <el-dialog
          v-model="showOptimizeModal"
          title="Optimize Portfolio"
          width="500px"
          :close-on-click-modal="false"
        >
          <el-form :model="optimizeForm" label-width="120px">
            <el-form-item label="Optimize Target">
              <span style="font-weight:bold;">{{ optimizeForm.metric }}</span>
            </el-form-item>
            <el-form-item label="Start Date">
              <el-date-picker v-model="optimizeForm.start_date" type="date" style="width: 100%" />
            </el-form-item>
            <el-form-item label="End Date">
              <el-date-picker v-model="optimizeForm.end_date" type="date" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Allow Short">
              <el-switch v-model="optimizeForm.allow_short" />
            </el-form-item>
          </el-form>
          <template #footer>
            <div class="dialog-footer-btns">
              <el-button class="round-btn info-btn" @click="showOptimizeModal = false">Cancel</el-button>
              <el-button type="primary" class="round-btn gradient-btn" :loading="optimizing" @click="submitOptimize">Start Optimize</el-button>
            </div>
          </template>
          <div v-if="optimizeResult">
            <h4>Optimize Result</h4>
            <div v-for="(weight, ticker) in optimizeResult.optimized_weights" :key="ticker">
              {{ ticker }}: {{ (weight * 100).toFixed(2) }}%
            </div>
            <el-button type="success" class="round-btn green-gradient-btn" @click="applyOptimizedWeights" style="margin-top: 12px;">Apply Optimized Weights</el-button>
          </div>
        </el-dialog>
      </div>

      <div v-else class="questionnaire-form">
        <el-form
          ref="questionnaireForm"
          :model="formData"
          :rules="rules"
          label-position="top"
          class="questionnaire-form-content"
        >
          <div
            v-for="(question, questionId) in questions"
            :key="questionId"
            class="question-item"
          >
            <h4 class="question-title">{{ question.question }}</h4>
            <el-form-item
              :prop="`answers.${questionId}`"
              :rules="[{ required: true, message: 'Please select an answer', trigger: 'change' }]"
            >
              <el-checkbox-group
                v-if="question.multi"
                v-model="formData.answers[questionId]"
                class="answer-options"
              >
                <el-checkbox
                  v-for="(answer, index) in question.answers"
                  :key="index"
                  :label="answer"
                  class="answer-option"
                >
                  {{ answer }}
                </el-checkbox>
              </el-checkbox-group>
              <el-radio-group
                v-else
                v-model="formData.answers[questionId]"
                class="answer-options"
              >
                <el-radio
                  v-for="(answer, index) in question.answers"
                  :key="index"
                  :label="answer"
                  class="answer-option"
                >
                  {{ answer }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </div>

          <div class="form-actions">
            <el-button
              type="primary"
              size="large"
              class="round-btn gradient-btn"
              :loading="submitting"
              @click="submitQuestionnaire"
            >
              Submit questionnaire
            </el-button>
            <el-button
              size="large"
              class="round-btn info-btn"
              @click="loadUserResponse"
            >
              Load saved answers
            </el-button>
          </div>
        </el-form>
      </div>
    </el-card>

    <!-- View answers dialog -->
    <el-dialog
      v-model="showResponsesDialog"
      title="My questionnaire answers"
      width="600px"
      class="enhanced-dialog"
    >
      <div v-if="userResponses" class="responses-container">
        <div
          v-for="(question, questionId) in questions"
          :key="questionId"
          class="response-item"
        >
          <h5>{{ question.question }}</h5>
          <p class="response-answer">
            <template v-if="question.multi">
              <el-tag
                v-for="(ans, idx) in userResponses.answers[questionId]"
                :key="idx"
                type="info"
                style="margin-right: 4px;"
              >{{ ans }}</el-tag>
            </template>
            <template v-else>
              {{ userResponses.answers[questionId] }}
            </template>
          </p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showResponsesDialog = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { questionnaireService } from '../services/api';
import { portfolioService } from '../services/api';

const loading = ref(true);
const submitting = ref(false);
const submitted = ref(false);
const showResponsesDialog = ref(false);
const questions = ref({});
const userResponses = ref(null);
const questionnaireForm = ref(null);
const aiStockSuggestion = ref(null);
const aiMetricSuggestion = ref(null);
const aiLoading = ref(false);
const showCreatePortfolioModal = ref(false);
const creatingPortfolio = ref(false);
const portfolioCreated = ref(false);
const optimizeResult = ref(null);
const portfolioFormRef = ref(null);
const showOptimizeModal = ref(false);
const optimizing = ref(false);
const createdPortfolioId = ref(null);
const router = useRouter();

const formData = reactive({
  answers: {}
});

const rules = {
  answers: {
    type: 'object',
    required: true
  }
};

const newPortfolio = ref({
  name: '',
  start_date: '',
  items: []
});

const portfolioRules = {
  name: [{ required: true, message: 'Please enter portfolio name', trigger: 'blur' }],
  start_date: [{ required: true, message: 'Please select start date', trigger: 'change' }]
};

onMounted(async () => {
  await loadQuestions();
  await loadUserResponse();
});

const loadQuestions = async () => {
  try {
    loading.value = true;
    const data = await questionnaireService.getQuestionnaires();
    questions.value = data;
    
    // Initialize form data
    Object.keys(data).forEach(questionId => {
      if (data[questionId].multi) {
        formData.answers[questionId] = [];
      } else {
        formData.answers[questionId] = '';
      }
    });
  } catch (error) {
    ElMessage.error('Failed to load questionnaire');
    console.error('Error loading questions:', error);
  } finally {
    loading.value = false;
  }
};

const loadUserResponse = async () => {
  try {
    const response = await questionnaireService.getUserResponse();
    if (response && response.questionnaire_response) {
      const formattedAnswers = {};
      Object.keys(response.questionnaire_response).forEach(questionId => {
        const answerArray = response.questionnaire_response[questionId];
        if (questions.value[questionId]?.multi) {
          formattedAnswers[questionId] = answerArray || [];
        } else {
          formattedAnswers[questionId] = answerArray[0] || '';
        }
      });
      
      userResponses.value = { answers: formattedAnswers };
      
      // If the user has already answered, fill in the form
      Object.keys(formattedAnswers).forEach(questionId => {
        if (formData.answers.hasOwnProperty(questionId)) {
          formData.answers[questionId] = formattedAnswers[questionId];
        }
      });
    }
  } catch (error) {
    // The user may not have answered the questionnaire yet, which is normal
    console.log('No existing responses found');
  }
};

const fetchAISuggestions = async () => {
  aiLoading.value = true;
  try {
    await questionnaireService.generateStockSuggestions();
    await questionnaireService.generateMetricSuggestions();
    const stockRes = await questionnaireService.getStockSuggestions();
    aiStockSuggestion.value = stockRes.result;
    const metricRes = await questionnaireService.getMetricSuggestions();
    aiMetricSuggestion.value = metricRes.result;
  } catch (e) {
    aiStockSuggestion.value = null;
    aiMetricSuggestion.value = null;
  } finally {
    aiLoading.value = false;
  }
};

const submitQuestionnaire = async () => {
  try {
    await questionnaireForm.value.validate();
    submitting.value = true;
    // Construct submission format: multi-choice questions as arrays, single-choice questions as single-element arrays
    const answersArray = Object.keys(formData.answers).map(questionId => {
      const answer = formData.answers[questionId];
      if (questions.value[questionId]?.multi) {
        return answer;
      } else {
        return [answer];
      }
    });
    await questionnaireService.submitQuestionnaireRaw(answersArray);
    ElMessage.success('Questionnaire submitted successfully!');
    submitted.value = true;
    userResponses.value = { answers: { ...formData.answers } };
    await fetchAISuggestions();
  } catch (error) {
    if (error.message) {
      ElMessage.error(error.message);
    } else {
      ElMessage.error('Failed to submit questionnaire, please try again');
    }
    console.error('Error submitting questionnaire:', error);
  } finally {
    submitting.value = false;
  }
};

const resetQuestionnaire = () => {
  submitted.value = false;
  Object.keys(questions.value).forEach(questionId => {
    if (questions.value[questionId].multi) {
      formData.answers[questionId] = [];
    } else {
      formData.answers[questionId] = '';
    }
  });
  questionnaireForm.value?.clearValidate();
};

const viewResponses = () => {
  showResponsesDialog.value = true;
};

const submitPortfolio = async () => {
  await portfolioFormRef.value.validate();
  creatingPortfolio.value = true;
  try {
    // Filter out empty rows
    const validItems = newPortfolio.value.items.filter(item => item.ticker && item.weight !== null && item.weight !== '');
    const tickers = validItems.map(item => item.ticker);
    const weights = validItems.map(item => parseFloat(item.weight));
    const totalWeight = weights.reduce((a, b) => a + b, 0);

    if (tickers.length === 0) {
      ElMessage.error('Please select at least one stock');
      return;
    }
    if (tickers.length !== weights.length) {
      ElMessage.error('Stock and weight number do not match');
      return;
    }
    if (Math.abs(totalWeight - 1) > 0.0001) {
      ElMessage.error('Weight sum must be 1');
      return;
    }
    if (!newPortfolio.value.name || !newPortfolio.value.start_date) {
      ElMessage.error('Please fill in all information');
      return;
    }

    // Date formatting
    let formattedDate = newPortfolio.value.start_date;
    if (formattedDate instanceof Date) {
      formattedDate = formattedDate.toISOString().split('T')[0];
    }

    const payload = {
      name: newPortfolio.value.name,
      start_date: formattedDate,
      tickers,
      weights
    };
    const res = await portfolioService.createPortfolio(payload);
    console.log('Create portfolio return:', res);

    // Correctly extract ID
    createdPortfolioId.value = res.data?.portfolio?.ptfid || res.data?.portfolio?.id || null;
    console.log('New portfolio ID:', createdPortfolioId.value);

    ElMessage.success('Portfolio created successfully');
    showCreatePortfolioModal.value = false;
    portfolioCreated.value = true;
  } catch (e) {
    ElMessage.error('Create failed: ' + (e.response?.data?.detail || e.message));
  } finally {
    creatingPortfolio.value = false;
  }
};

const optimizeForm = ref({
  metric: aiMetricSuggestion.value?.recommended_metric || 'sharpe',
  start_date: '',
  end_date: '',
  allow_short: false
});

const submitOptimize = async () => {
  optimizing.value = true;
  try {
    const tickers = newPortfolio.value.items.map(item => item.ticker);
    const params = {
      tickers,
      metric: getBackendMetric(optimizeForm.value.metric),
      start_date: optimizeForm.value.start_date,
      end_date: optimizeForm.value.end_date,
      allow_short: optimizeForm.value.allow_short
    };
    console.log('Optimize parameters:', params);
    const res = await portfolioService.optimizeNewPortfolio(params);
    optimizeResult.value = res.data;
    ElMessage.success('Optimize completed');
  } catch (e) {
    ElMessage.error('Optimize failed: ' + (e.response?.data?.detail || e.message));
  } finally {
    optimizing.value = false;
  }
};

const applyOptimizedWeights = async () => {
  try {
    if (!createdPortfolioId.value) {
      ElMessage.error('Portfolio ID not found, cannot update');
      return;
    }
    const tickers = Object.keys(optimizeResult.value.optimized_weights);
    const weights = tickers.map(ticker => parseFloat(optimizeResult.value.optimized_weights[ticker]));

    // check
    if (tickers.length === 0 || weights.length === 0) {
      ElMessage.error('Please check stock and weight');
      return;
    }
    if (tickers.length !== weights.length) {
      ElMessage.error('Stock and weight number do not match');
      return;
    }
    if (weights.some(w => isNaN(w))) {
      ElMessage.error('Weight must be a number');
      return;
    }
    const totalWeight = weights.reduce((a, b) => a + b, 0);
    if (Math.abs(totalWeight - 1) > 0.0001) {
      ElMessage.error('Weight sum must be 1');
      return;
    }

    // Directly call updatePortfolio
    await portfolioService.updatePortfolio(createdPortfolioId.value, {
      tickers,
      weights
    });
    ElMessage.success('Optimized weights updated successfully');
    // redirect to portfolio page
    setTimeout(() => {
      router.push('/portfolio');
    }, 800);
  } catch (e) {
    ElMessage.error('Apply failed: ' + (e.response?.data?.detail || e.message));
  }
};

// Check if a ticker has been selected (except the current row)
const isTickerSelected = (ticker, currentIndex) => {
  return newPortfolio.value.items.some((item, idx) => idx !== currentIndex && item.ticker === ticker);
};

// Add/delete stock row
const addTicker = () => {
  if (newPortfolio.value.items.length < aiStockSuggestion.value.tickers.length) {
    newPortfolio.value.items.push({ ticker: '', weight: 0 });
  }
};
const removeTicker = (idx) => {
  if (newPortfolio.value.items.length > 1) {
    newPortfolio.value.items.splice(idx, 1);
  }
};

// Automatically fill one row when initialized
watch(
  () => aiStockSuggestion.value,
  (val) => {
    if (val && val.tickers && newPortfolio.value.items.length === 0) {
      newPortfolio.value.items = [{ ticker: '', weight: 0 }];
    }
  },
  { immediate: true }
);

// If aiMetricSuggestion is asynchronous, watch needs to automatically assign values
watch(
  () => aiMetricSuggestion.value,
  (val) => {
    if (val && val.recommended_metric) {
      optimizeForm.value.metric = val.recommended_metric;
    }
  },
  { immediate: true }
);

const metricMap = {
  'sharpe': 'sharpe',
  'sortino': 'sortino',
  'total_return': 'total return',
  'total return': 'total return',
  'weekly_return': 'weekly return',
  'weekly return': 'weekly return',
  'daily_return': 'daily return',
  'daily return': 'daily return'
};

function getBackendMetric(metric) {
  return metricMap[metric] || metric;
}
</script>

<style scoped>
.questionnaire-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: calc(100vh - 120px);
}

.questionnaire-card.enhanced-card {
  width: 100%;
  border-radius: 18px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: none;
  background: #fff;
  transition: all 0.3s ease;
}

.questionnaire-card.enhanced-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.card-header {
  text-align: center;
}

.card-header h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.loading-container {
  padding: 20px;
}

.questionnaire-form {
  padding: 20px 0;
}

.question-item {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #409eff;
  transition: all 0.3s ease;
}

.question-item:hover {
  background-color: #f0f7ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
}

.question-title {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.answer-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}

.answer-option {
  margin: 0;
  padding: 12px 16px;
  background-color: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
  width: 100%;
  text-align: left;
  display: flex;
  align-items: flex-start;
}

.answer-option :deep(.el-radio__input) {
  margin-top: 2px;
  flex-shrink: 0;
}

.answer-option :deep(.el-radio__label) {
  padding-left: 8px;
  line-height: 1.5;
  text-align: left;
  word-wrap: break-word;
  flex: 1;
}

.answer-option:hover {
  border-color: #409eff;
  background-color: #f0f7ff;
  transform: translateX(4px);
}

.answer-option.is-checked {
  border-color: #409eff;
  background-color: #f0f7ff;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.submitted-container {
  padding: 40px 20px;
  text-align: center;
}

.responses-container {
  max-height: 400px;
  overflow-y: auto;
}

.response-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.response-item h5 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 14px;
  font-weight: 600;
}

.response-answer {
  margin: 0;
  color: #409eff;
  font-weight: 500;
  line-height: 1.4;
}

.round-btn {
  border-radius: 18px !important;
  font-weight: 500;
  padding: 8px 22px !important;
  font-size: 15px;
}

.gradient-btn {
  background: linear-gradient(90deg, #36cfc9 0%, #409eff 100%) !important;
  color: #fff !important;
  box-shadow: 0 2px 8px #36cfc933;
  border: none !important;
  transition: background 0.2s, box-shadow 0.2s;
}

.gradient-btn:hover {
  background: linear-gradient(90deg, #66b1ff 0%, #5cdbd3 100%) !important;
  box-shadow: 0 4px 16px #409eff33;
}

.info-btn {
  background: #e6f7ff !important;
  color: #409eff !important;
  border: 1px solid #b3e5fc !important;
  transition: background 0.2s, color 0.2s;
}

.info-btn:hover {
  background: #b3e5fc !important;
  color: #fff !important;
}

.enhanced-dialog :deep(.el-dialog) {
  border-radius: 18px;
}

.fade-in {
  animation: fadeIn 0.7s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive design */
@media (max-width: 768px) {
  .questionnaire-container {
    padding: 10px;
    max-width: 100%;
  }
  
  .question-item {
    padding: 15px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .answer-option {
    padding: 10px 12px;
  }
  
  .card-header h3 {
    font-size: 20px;
  }
}

@media (min-width: 1200px) {
  .questionnaire-container {
    max-width: 1000px;
  }
}

@media (min-width: 1600px) {
  .questionnaire-container {
    max-width: 1100px;
  }
}

.ai-suggestion-block {
  margin: 24px auto 0 auto;
  max-width: 600px;
  background: #f8f9fa;
  border-radius: 10px;
  padding: 18px 24px;
  box-shadow: 0 2px 8px #409eff11;
}

.create-portfolio-dialog >>> .el-dialog {
  border-radius: 18px;
}
.create-portfolio-form {
  padding: 16px 8px 0 8px;
}
.portfolio-row-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.portfolio-row {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  align-items: center;
  width: 100%;
}
.portfolio-row .el-select,
.portfolio-row .el-input-number {
  flex-shrink: 0;
}
.portfolio-row .delete-btn {
  margin-left: 8px;
  min-width: 70px;
}
.dialog-footer-btns {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 8px 0 0 0;
}
@media (max-width: 900px) {
  .create-portfolio-dialog >>> .el-dialog {
    width: 98vw !important;
    min-width: unset !important;
    max-width: 100vw !important;
  }
  .portfolio-row {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .portfolio-row-list {
    gap: 0;
  }
  .dialog-footer-btns {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
}
.remove-btn {
  background: linear-gradient(90deg, #f56c6c 0%, #ff9c9c 100%) !important;
  border: none !important;
  color: white !important;
}
.remove-btn:hover {
  background: linear-gradient(90deg, #f78989 0%, #ffb3b3 100%) !important;
  color: white !important;
}
.portfolio-btn-group {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  margin-top: 24px;
  flex-wrap: wrap;
}
@media (max-width: 600px) {
  .portfolio-btn-group {
    flex-direction: column;
    gap: 12px;
    margin-top: 16px;
  }
}
.green-gradient-btn {
  background: linear-gradient(90deg, #67c23a 0%, #b7eb8f 100%) !important;
  border: none !important;
  color: white !important;
}
.green-gradient-btn:hover {
  background: linear-gradient(90deg, #95de64 0%, #eaffd0 100%) !important;
  color: white !important;
}
</style> 