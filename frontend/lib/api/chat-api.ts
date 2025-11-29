import axios from "axios";

const baseUrl = process.env.NEXT_PUBLIC_CHAT_API_BASE_URL;
const chatAxios = axios.create({
  baseURL: baseUrl,
});

// Health check
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await chatAxios.get("/health");
    return response.status === 200 && response.data.status === "ok";
  } catch (error) {
    console.error("Health check failed:", error);
    return false;
  }
};

// Send message to chatbot
interface ChatTurn {
    role: string;
    content: string;
}

interface ChatbotMessageReq {
    question: string;
    history: ChatTurn[];
    return_chunks?: boolean;
}

export const sendMessageToChatbot = async (question: string): Promise<{ answer: string; courseId: number }> => {
  try {
    const cur_history = localStorage.getItem("chatHistory");
    const payload: ChatbotMessageReq = {
      question,
      history: cur_history ? JSON.parse(cur_history) : [],
      return_chunks: true,
    };
    const response = await chatAxios.post("/ask", payload);
    const answer = response.data.answer as string;
    const courseId = response.data.retrieved_chunks[0].course_id;

    console.log("Chatbot response:", response.data);
    
    return { answer, courseId }
  } catch (error) {
    console.error("Error sending message to chatbot:", error);
    throw new Error("Có lỗi xảy ra!")
  }
}