function Message({ msg }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent:
          msg.sender === "user"
            ? "flex-end"
            : "flex-start",
        marginBottom: "15px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}
      >
        {msg.sender === "bot" && (
          <div
            style={{
              width: "35px",
              height: "35px",
              borderRadius: "50%",
              backgroundColor: "#d1d5db",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            🤖
          </div>
        )}

        <div
          style={{
            backgroundColor:
              msg.sender === "user"
                ? "#2563eb"
                : "#e5e7eb",

            color:
              msg.sender === "user"
                ? "white"
                : "black",

            padding: "12px 16px",
            borderRadius: "15px",
            maxWidth: "300px",
          }}
        >
          {msg.text}
        </div>

        {msg.sender === "user" && (
          <div
            style={{
              width: "35px",
              height: "35px",
              borderRadius: "50%",
              backgroundColor: "#2563eb",
              color: "white",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            👤
          </div>
        )}
      </div>
    </div>
  );
}

export default Message;