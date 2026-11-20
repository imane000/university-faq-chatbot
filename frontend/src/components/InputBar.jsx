function InputBar({
  message,
  setMessage,
  sendMessage,
  isTyping,
}) {

  // ENTRÉE CLAVIER
  const handleKeyDown = (e) => {

    if (e.key === "Enter" && !e.nativeEvent.isComposing && !isTyping) {
      sendMessage();
    }

  };

  return (

    <div
      style={{
        display: "flex",
        gap: "15px",
        marginTop: "20px",
      }}
    >

      {/* INPUT */}
      <input
        type="text"
        aria-label="Votre question universitaire"
        maxLength={2000}
        disabled={isTyping}
        placeholder="Posez votre question..."
        value={message}
        onChange={(e) =>
          setMessage(e.target.value)
        }
        onKeyDown={handleKeyDown}
        style={{
          flex: 1,
          padding: "18px",
          borderRadius: "20px",
          border: "2px solid #222",
          fontSize: "18px",
          outline: "none",
        }}
      />

      {/* BUTTON */}
      <button
        onClick={() => sendMessage()}
        disabled={isTyping}
        style={{
          backgroundColor:
  isTyping ? "#9ca3af" : "#2563eb",
          color: "white",
          border: "none",
          padding: "18px 30px",
          borderRadius: "18px",
          cursor:
  isTyping ? "not-allowed" : "pointer",
          fontSize: "20px",
          fontWeight: "bold",
        }}
      >
        Envoyer
      </button>

    </div>
  );
}

export default InputBar;