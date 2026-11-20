import { sendMessage as sendToAPI } from "./services/api";
import { useState, useEffect, useRef } from "react";

import Sidebar from "./components/Sidebar";
import ChatBox from "./components/ChatBox";
import InputBar from "./components/InputBar";

const createConversation = () => ({
  id: Date.now(),
  title: "Nouvelle conversation",
  messages: [{ text: "Bonjour 👋", sender: "bot" }],
});

const loadConversations = () => {
  try {
    const saved = JSON.parse(localStorage.getItem("conversations"));
    if (Array.isArray(saved) && saved.length && saved.every((conv) =>
      typeof conv?.id === "number" && typeof conv.title === "string" &&
      Array.isArray(conv.messages) && conv.messages.every((msg) =>
        typeof msg?.text === "string" && ["bot", "user"].includes(msg.sender)))) {
      return saved;
    }
  } catch { /* Invalid or unavailable browser storage starts a fresh conversation. */ }
  return [createConversation()];
};

function App() {

  // INPUT
  const [message, setMessage] = useState("");

  // CONVERSATIONS
  const [conversations, setConversations] = useState(loadConversations);
  const [currentConversationId, setCurrentConversationId] =
    useState(() => conversations[0].id);
  const requestInFlight = useRef(false);

  // TYPING
  const [isTyping, setIsTyping] =
    useState(false);

  // AUTO SCROLL
  const messagesEndRef = useRef(null);

  // CURRENT CHAT
  const currentConversation =
    conversations.find(
      (conv) =>
        conv.id === currentConversationId
    );

  // AUTO SCROLL + SAVE
  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });

    try {
      localStorage.setItem("conversations", JSON.stringify(conversations));
    } catch { /* Chat remains usable if storage is full or disabled. */ }

  }, [conversations, isTyping]);

  // NEW CONVERSATION
  const newConversation = () => {

    const newConv = createConversation();

    setConversations((prev) => [
      ...prev,
      newConv,
    ]);

    setCurrentConversationId(newConv.id);

  };

  // DELETE CONVERSATION
  const deleteConversation = (id) => {

    const updated = conversations.filter((conv) => conv.id !== id);
    const remaining = updated.length ? updated : [createConversation()];
    setConversations(remaining);
    if (id === currentConversationId) setCurrentConversationId(remaining[0].id);
  };

  // SELECT CONVERSATION
  const selectConversation = (id) => {

    setCurrentConversationId(id);

  };

  // QUICK QUESTION
  const quickQuestion = (question) => {

    sendMessage(question);
  };

  // SEND MESSAGE
  const sendMessage = async (customMessage) => {

    const finalMessage =
      customMessage || message;

    if (!finalMessage.trim() || requestInFlight.current) return;
    requestInFlight.current = true;

    // USER MESSAGE
    const userMessage = {
      text: finalMessage,
      sender: "user",
    };

    // UPDATE USER MESSAGE
    setConversations((prev) =>
      prev.map((conv) => {

        if (
          conv.id === currentConversationId
        ) {

          return {

            ...conv,

            title:
              conv.title ===
              "Nouvelle conversation"
                ? finalMessage
                : conv.title,

            messages: [
              ...conv.messages,
              userMessage,
            ],
          };

        }

        return conv;

      })
    );

    setMessage("");

    setIsTyping(true);

    try {

      const data =
        await sendToAPI(finalMessage);

      const botMessage = {
        text: data.response,
        sender: "bot",
        sources: data.sources || [],
      };

      setConversations((prev) =>
        prev.map((conv) => {

          if (
            conv.id === currentConversationId
          ) {

            return {

              ...conv,

              messages: [
                ...conv.messages,
                botMessage,
              ],
            };

          }

          return conv;

        })
      );

    } catch (error) {

      const errorMessage = {
        text: error.message || "Service indisponible. Réessayez.",
        sender: "bot",
      };

      setConversations((prev) =>
        prev.map((conv) => {

          if (
            conv.id === currentConversationId
          ) {

            return {

              ...conv,

              messages: [
                ...conv.messages,
                errorMessage,
              ],
            };

          }

          return conv;

        })
      );

    }

    requestInFlight.current = false;
    setIsTyping(false);

  };

  return (

    <div
      style={{
        backgroundColor: "#f3f4f6",
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        padding: "10px",
        paddingTop: "30px",
        fontFamily: "Arial",
      }}
    >

      <div
        style={{
          display: "flex",
          gap: "20px",
          alignItems: "flex-start",
        }}
      >

        {/* SIDEBAR */}
        <Sidebar
          newConversation={newConversation}
          quickQuestion={quickQuestion}
          conversations={conversations}
          currentConversationId={
            currentConversationId
          }
          selectConversation={
            selectConversation
          }
          deleteConversation={
            deleteConversation
          }
        />

        {/* CHAT */}
        <div
          style={{
            backgroundColor: "white",
            width: "420px",
            height: "600px",
            borderRadius: "20px",
            padding: "20px",
            boxShadow:
              "0px 0px 15px rgba(0,0,0,0.1)",
            display: "flex",
            flexDirection: "column",
          }}
        >

          {/* TITLE */}
          <h1
            style={{
              textAlign: "center",
              fontSize: "28px",
              marginBottom: "20px",
            }}
          >
            University FAQ Chatbot
          </h1>

          {/* CHAT AREA */}
          <ChatBox
            messages={
              currentConversation.messages
            }
            isTyping={isTyping}
            messagesEndRef={messagesEndRef}
          />

          {/* INPUT */}
          <InputBar
            message={message}
            setMessage={setMessage}
            sendMessage={sendMessage}
            isTyping={isTyping}
          />

        </div>

      </div>

    </div>
  );
}

export default App;