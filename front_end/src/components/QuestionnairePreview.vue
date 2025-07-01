<template>
  <div class="questionnaire-preview">
    <el-card class="preview-card">
      <template #header>
        <div class="card-header">
          <span>Questionnaire</span>
          <el-tag 
            :type="hasCompleted ? 'success' : 'warning'" 
            size="small"
          >
            {{ hasCompleted ? 'finished' : 'not finished' }}
          </el-tag>
        </div>
      </template>
      
      <div class="preview-content">
        <div class="preview-text">
          <h4>Personalized investment advice</h4>
          <p>By answering 6 simple questions, you can get personalized investment advice and stock recommendations.</p>
        </div>
        
        <div class="preview-actions">
          <el-button 
            type="primary" 
            class="round-btn gradient-btn"
            @click="router.push('/questionnaire')"
            :icon="hasCompleted ? 'Edit' : 'Document'"
          >
            {{ hasCompleted ? 'Re-fill' : 'Start' }}
          </el-button>
          
          <el-button 
            v-if="hasCompleted" 
            type="info" 
            class="round-btn info-btn"
            @click="viewResponses"
            icon="View"
          >
            View answers and AI suggestions
          </el-button>
        </div>
        
        <div v-if="hasCompleted" class="completion-info">
          <el-icon color="#67c23a"><Check /></el-icon>
          <span>You have completed the questionnaire, and the system will provide personalized advice.</span>
        </div>
      </div>
    </el-card>

    <!-- View answers dialog -->
    <el-dialog
      v-model="showResponsesDialog"
      title="My questionnaire answers"
      width="600px"
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
        <el-button type="primary" @click="router.push('/questionnaire')">Re-fill</el-button>
      </template>
      <div v-if="showResponsesDialog">
        <div v-if="aiLoading" class="ai-suggestion-block" style="text-align:center;">
          <el-icon class="is-loading" style="font-size:28px;margin-bottom:8px;"/>
          <div>AI suggestions loading...</div>
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
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Check, Edit, Document, View } from '@element-plus/icons-vue';
import { questionnaireService } from '../services/api';

const router = useRouter();
const questions = ref({});
const userResponses = ref(null);
const showResponsesDialog = ref(false);
const aiStockSuggestion = ref(null);
const aiMetricSuggestion = ref(null);
const aiLoading = ref(false);

const hasCompleted = computed(() => {
  return userResponses.value && userResponses.value.answers && 
         Object.keys(userResponses.value.answers).length > 0;
});

onMounted(async () => {
  await loadQuestions();
  await loadUserResponse();
});

const loadQuestions = async () => {
  try {
    const data = await questionnaireService.getQuestionnaires();
    questions.value = data;
  } catch (error) {
    console.error('Error loading questions:', error);
  }
};

const loadUserResponse = async () => {
  try {
    const response = await questionnaireService.getUserResponse();
    if (response && response.questionnaire_response) {
      // Convert the array format returned by the backend to the object format used by the frontend
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
    }
  } catch (error) {
    // The user may not have answered the questionnaire yet, which is normal
    console.log('No existing responses found');
  }
};

const loadAISuggestions = async () => {
  aiLoading.value = true;
  try {
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

const viewResponses = () => {
  showResponsesDialog.value = true;
  loadAISuggestions();
};
</script>

<style scoped>
.questionnaire-preview {
  width: 100%;
}

.preview-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.preview-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #2c3e50;
}

.preview-content {
  padding: 10px 0;
}

.preview-text h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.preview-text p {
  margin: 0 0 15px 0;
  color: #7f8c8d;
  font-size: 14px;
  line-height: 1.5;
}

.preview-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.completion-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background-color: #f0f9ff;
  border-radius: 6px;
  color: #67c23a;
  font-size: 14px;
}

.responses-container {
  max-height: 400px;
  overflow-y: auto;
}

.response-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-actions {
    flex-direction: column;
  }
  
  .preview-actions .el-button {
    width: 100%;
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
</style> 