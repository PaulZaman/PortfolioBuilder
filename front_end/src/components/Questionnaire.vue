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
              <el-radio-group
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
          <p class="response-answer">{{ userResponses.answers[questionId] }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showResponsesDialog = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { questionnaireService } from '../services/api';

const loading = ref(true);
const submitting = ref(false);
const submitted = ref(false);
const showResponsesDialog = ref(false);
const questions = ref({});
const userResponses = ref(null);
const questionnaireForm = ref(null);

const formData = reactive({
  answers: {}
});

const rules = {
  answers: {
    type: 'object',
    required: true
  }
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
    
    // 初始化表单数据
    Object.keys(data).forEach(questionId => {
      formData.answers[questionId] = '';
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
      // Convert the array format returned by the backend to the object format used by the frontend
      const formattedAnswers = {};
      Object.keys(response.questionnaire_response).forEach(questionId => {
        const answerArray = response.questionnaire_response[questionId];
        // Take the first answer (because the frontend only supports single selection)
        formattedAnswers[questionId] = answerArray[0] || '';
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

const submitQuestionnaire = async () => {
  try {
    await questionnaireForm.value.validate();
    submitting.value = true;
    
    await questionnaireService.submitQuestionnaire(formData.answers);
    
    ElMessage.success('Questionnaire submitted successfully!');
    submitted.value = true;
    userResponses.value = { answers: { ...formData.answers } };
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
    formData.answers[questionId] = '';
  });
  questionnaireForm.value?.clearValidate();
};

const viewResponses = () => {
  showResponsesDialog.value = true;
};
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
</style> 