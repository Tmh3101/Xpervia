import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import MessageList from "./MessageList";
import ChatLauncher from "./ChatLauncher";
import { sendMessageToChatbot, healthCheck } from "@/lib/api/chat-api";
import { Send, ArrowDownToLine } from "lucide-react"
import chatBg from "@/public/chat-bg.png"
import logo from "@/public/logo-ngang.png";

type ChatTurn = { role: "user" | "assistant"; content: string, courseId?: number };

const STORAGE_KEY = "chatHistory";

function loadMessagesFromStorage(): ChatTurn[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as ChatTurn[];
  } catch {
    return [];
  }
}

function saveMessagesToStorage(msgs: ChatTurn[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(msgs.slice(-6)));
  } catch {
    /* silent */
  }
}

export const ChatWidget: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatTurn[]>(() => loadMessagesFromStorage());
  const [typing, setTyping] = useState(false);
  const [canScrollToBottom, setCanScrollToBottom] = useState(true);
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const mountedRef = useRef(false);
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const MAX_ROWS = 4;

  useEffect(() => {
    if (!mountedRef.current) return;
    saveMessagesToStorage(messages);
  }, [messages]);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const ok = await healthCheck();
        if (!mounted) return;
      } catch {
        // ignore
      }
    })();
    return () => { mounted = false; };
  }, []);

  const handleToggle = useCallback(() => setOpen((v) => !v), []);
  const handleManualScroll = useCallback((atBottom: boolean) => setCanScrollToBottom(atBottom), []);

  const scrollToBottom = useCallback((smooth = true) => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: smooth ? "smooth" : "auto" });
    setCanScrollToBottom(true);
  }, []);

  const send = useCallback(
    async (text: string) => {
      const userMsg: ChatTurn = { role: "user", content: text };
      setMessages((prev) => {
        const next = [...prev, userMsg];
        saveMessagesToStorage(next);
        return next;
      });

      setTyping(true);
      scrollToBottom(false);
      try {
        const { answer, courseId } = await sendMessageToChatbot(text);
        const assistantMsg: ChatTurn = { role: "assistant", content: answer || "Xin lỗi, hệ thống không trả lời được.", courseId };
        setMessages((prev) => {
          const next = [...prev, assistantMsg];
          saveMessagesToStorage(next);
          return next;
        });
        setTimeout(() => scrollToBottom(true), 50);
      } catch (err) {
        const errMsg: ChatTurn = {
          role: "assistant",
          content: err instanceof Error ? err.message : "Có lỗi xảy ra!",
        };
        setMessages((prev) => {
          const next = [...prev, errMsg];
          saveMessagesToStorage(next);
          return next;
        });
      } finally {
        setTyping(false);
      }
    },
    [scrollToBottom]
  );

    const resizeTextarea = useCallback(() => {
        const el = textareaRef.current;
        if (!el) return;
        el.style.height = "auto";

        const cs = window.getComputedStyle(el);
        const lineHeight = parseFloat(cs.lineHeight) || 20;
        const paddingTop = parseFloat(cs.paddingTop) || 0;
        const paddingBottom = parseFloat(cs.paddingBottom) || 0;
        const verticalPadding = paddingTop + paddingBottom;
        const maxHeight = lineHeight * MAX_ROWS + verticalPadding;
        const needed = el.scrollHeight;
        const newHeight = Math.min(needed, maxHeight);

        el.style.height = `${newHeight}px`;
        el.style.overflowY = needed > maxHeight ? "auto" : "hidden";
    }, []);

    useEffect(() => {
        requestAnimationFrame(() => resizeTextarea());
    }, [value, resizeTextarea]);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!typing && value.trim()) {
                send(value.trim());
                setValue("");
            }
        }
    };

  return (  
    <>
      <ChatLauncher open={open} onToggle={handleToggle} />

      {open && (
        <div
          className="fixed -right-14 bottom-20 z-[9999] w-full max-w-xs sm:max-w-sm md:max-w-md lg:max-w-md"
          style={{ maxHeight: "92vh" }}
        >
            <Card className="flex flex-col w-10/12 h-[60vh] sm:h-[78vh] md:h-[72vh] lg:h-[58vh] overflow-hidden shadow-2xl rounded-2xl">
                <CardHeader className="flex justify-between p-2 border-b bg-primary">
                    <Image
                      src={logo}
                      alt="Logo"
                      width={80}
                      height={80}
                      className="rounded-xl bg-white"
                    />
                </CardHeader>

                <CardContent
                    className="flex-1 p-0 relative min-h-0"
                    style={{
                        backgroundImage: `url(${chatBg.src})`,
                        backgroundSize: "cover",
                        backgroundRepeat: "no-repeat",
                        backgroundPosition: "center top",
                    }}
                >
                    <MessageList messages={messages} typing={typing} scrollerRef={scrollerRef} onManualScroll={handleManualScroll} />
                    {!canScrollToBottom && (
                        <div className="absolute left-1/2 bottom-4 z-10 -translate-x-1/2">
                            <Button
                                size="sm"
                                onClick={() => scrollToBottom(true)}
                                className="rounded-full bg-white shadow-lg text-primary hover:bg-white hover:text-primary"
                            >
                                <ArrowDownToLine />
                            </Button>
                        </div>
                    )}
                </CardContent>

                <CardFooter className="sticky bottom-0 z-10 border-t bg-popover p-3">
                    <div className="w-full flex items-end gap-3">
                        <textarea
                            ref={textareaRef}
                            value={value}
                            onChange={(e) => {
                                setValue(e.target.value);
                                requestAnimationFrame(() => resizeTextarea());
                            }}
                            onKeyDown={handleKeyDown}
                            placeholder="Nhập câu hỏi..."
                            maxLength={64}
                            disabled={typing}
                            className="flex-1 min-h-[38px] max-h-[96px] resize-none rounded-lg border input-border px-3 py-2 text-sm leading-6 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                        />
                        <Button
                            onClick={() => {
                                if (!typing && value.trim()) {
                                    send(value.trim());
                                    setValue("");
                                }
                            }}
                            disabled={typing || value.trim().length === 0}
                            aria-label="Gửi"
                            className="rounded-full p-2 w-11 h-11 flex items-center justify-center"
                        >
                            <Send className="w-4 h-4" />
                        </Button>
                    </div>
                </CardFooter>
            </Card>
        </div>
      )}
    </>
  );
};

export default ChatWidget;