import React, { useEffect, useRef } from "react";
import Image from "next/image";
import { Avatar } from "@/components/ui/avatar";
import chatbotAvatar from "@/public/chatbot-avt.png";
import ChatCourseCard from "./CourseCard";

type ChatTurn = { role: "user" | "assistant"; content: string, courseId?: number };

/* Typing indicator: three animated dashes */
const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-center space-x-1">
      <span className="w-3 h-1 bg-current rounded-sm inline-block animate-pulse" style={{ animationDelay: "0s" }} />
      <span className="w-3 h-1 bg-current rounded-sm inline-block animate-pulse" style={{ animationDelay: "0.12s" }} />
      <span className="w-3 h-1 bg-current rounded-sm inline-block animate-pulse" style={{ animationDelay: "0.24s" }} />
    </div>
  );
};

const MessageBubble: React.FC<{ m: ChatTurn }> = ({ m }) => {
  const isUser = m.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} items-end`}> 
      {!isUser && (
        <Avatar className="mr-2 w-8 h-8 flex-shrink-0">
          <Image src={chatbotAvatar} alt="Chatbot Avatar" />
        </Avatar>
      )}

      <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`max-w-[76%] break-words px-3 py-2 rounded-lg text-sm whitespace-pre-wrap border border-primary ${
            isUser ? "bg-primary text-primary-foreground rounded-br-none" : "bg-white text-foreground rounded-bl-none"
          }`}
        >
          {m.content}
        </div>

        {/* Inline compact course card for assistant messages that reference a course */}
        {!isUser && m.courseId && (
          <div className="max-w-[76%]">
            <ChatCourseCard courseId={m.courseId} />
          </div>
        )}
      </div>
    </div>
  );
};

const MessageList: React.FC<{
  messages: ChatTurn[];
  typing: boolean;
  scrollerRef: React.RefObject<HTMLDivElement>;
  onManualScroll?: (atBottom: boolean) => void;
}> = ({ messages, typing, scrollerRef, onManualScroll }) => {
  const atBottomRef = useRef(true);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    if (atBottomRef.current) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [messages, typing, scrollerRef]);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    const onScroll = () => {
      const threshold = 48;
      const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight <= threshold;
      atBottomRef.current = atBottom;
      onManualScroll?.(atBottom);
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, [scrollerRef, onManualScroll]);

  return (
    <div ref={scrollerRef} className="h-full flex-1 overflow-auto p-4 space-y-3 min-h-0">
      {messages.length === 0 && (
        <div className="text-center text-sm text-muted-foreground mt-8">
            Xin chào! Hãy đặt câu hỏi về khóa học.
        </div>
      )}
      {messages.map((m, idx) => (
        <MessageBubble key={idx} m={m} />
      ))}

      {typing && (
        <div className="flex items-end justify-start mb-1">
            <Avatar className="mr-2 w-8 h-8 flex-shrink-0">
                <Image
                src={chatbotAvatar}
                alt="Chatbot Avatar"
                />
            </Avatar>
          <div className="bg-white border border-primary px-3 py-2 rounded-lg">
            <TypingIndicator />
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageList;