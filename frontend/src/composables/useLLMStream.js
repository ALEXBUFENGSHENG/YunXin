import { ref } from 'vue';
import { useLearningStore } from '../stores/learningStore';

export function useLLMStream() {
  const isLoading = ref(false);
  const store = useLearningStore();
  const baseUrl = '';

  const sendMessage = async (message, username, conversationId, deepThinking = false, type = 'chat') => {
    if (!message.trim()) return;

    const controller = new AbortController();
    const { signal } = controller;

    isLoading.value = true;
    store.addMessage({ role: 'user', content: message });
    
    try {
      const endpoint = type === 'learn' ? '/api/learn/stream' : '/api/chat/stream';
      const requestMode = type === 'learn' ? 'learn' : 'chat';
      
      const response = await fetch(`${baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          goal: message, 
          username, 
          conversation_id: parseInt(conversationId) || null, // 强制转为整数
          mode: requestMode, 
          deep_thinking: deepThinking 
        }),
        signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let aiMsgId = store.addMessage({ role: 'assistant', content: '' });

      let buffer = '';
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          const events = buffer.split('\n\n');
          buffer = events.pop() || '';
          
          for (const evt of events) {
              const line = evt.trim();
              if (!line.startsWith('data: ')) continue;
              
              const dataStr = line.slice(6).trim();
              if (!dataStr) continue;
              
              // 兼容 [DONE] 标记
              if (dataStr === '[DONE]') {
                  // 流正常结束
                  break; 
              }
              
              try {
                  const data = JSON.parse(dataStr);
                  
                  if (data.type === 'chunk') {
                      if (data.content === '[DONE]') continue; 
                      store.appendMessageContent(aiMsgId, data.content || '');
                  } else if (data.type === 'agent_data') {
                      console.log('[Frontend] Received agent_data:', data); // Add debug log
                      store.updateAgentData(data.agent, data.data);
                  } else if (data.type === 'agent_start') {
                      console.log('[Frontend] Received agent_start:', data); // Add debug log
                      store.setAgentStatus(data.agent, data.status);
                  } else if (data.type === 'error') {
                      // 处理后端明确传回的错误
                      store.addMessage({ role: 'system', content: `❌ ${data.message}` });
                  }
              } catch (e) {
                  console.warn('Stream parse error', e, dataStr);
              }
          }
        }
      } catch (readError) {
        console.error('Stream reading interrupted:', readError);
        throw readError; // Re-throw to be caught by outer catch
      }
    } catch (err) {
      console.error('Stream error:', err);
      store.addMessage({ role: 'system', content: `连接失败: ${err.message}` });
    } finally {
      isLoading.value = false;
      store.setAgentStatus('', 'idle');
    }
  };

  return { sendMessage, isLoading };
}
