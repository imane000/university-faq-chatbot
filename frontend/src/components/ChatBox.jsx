import Message from "./Message";

function ChatBox({
  messages,
  isTyping,
  messagesEndRef,
}) {
  return (
    <div
      style={{
        flex: 1,
        border: "1px solid #ddd",
        borderRadius: "15px",
        padding: "15px",
        overflowY: "auto",
        backgroundColor: "#fafafa",
      }}
    >
      {messages.map((msg, index) => (
        <Message key={index} msg={msg} />
      ))}

      {isTyping && (
        <div
          style={{
            backgroundColor: "#e5e7eb",
            padding: "10px 15px",
            borderRadius: "15px",
            width: "fit-content",
          }}
        >
          🤖 Bot écrit...
        </div>
      )}

      <div ref={messagesEndRef}></div>
    </div>
  );
}

export default ChatBox;