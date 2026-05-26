function Sidebar({

  newConversation,

  quickQuestion,

  conversations,

  currentConversationId,

  selectConversation,

  deleteConversation,

}) {

  return (

    <div
      style={{

        width: "220px",

        background:
          "linear-gradient(to bottom, #0f172a, #111827)",

        color: "white",

        padding: "20px",

        borderRadius: "20px",

        height: "600px",

        overflowY: "auto",

        boxShadow:
          "0px 0px 15px rgba(0,0,0,0.15)",

        display: "flex",

        flexDirection: "column",
      }}
    >

      {/* TITLE */}
      <h2
        style={{
          textAlign: "center",

          marginBottom: "20px",

          fontSize: "24px",

          fontWeight: "bold",
        }}
      >
        Chats
      </h2>

      {/* NEW CHAT */}
      <button
        onClick={newConversation}
        style={{
          width: "100%",

          padding: "13px",

          borderRadius: "14px",

          border: "none",

          background:
            "linear-gradient(to right, #2563eb, #3b82f6)",

          color: "white",

          fontWeight: "bold",

          cursor: "pointer",

          marginBottom: "25px",

          fontSize: "15px",

          boxShadow:
            "0px 4px 10px rgba(37,99,235,0.3)",
        }}
      >
        + Nouvelle conversation
      </button>

      {/* QUESTIONS RAPIDES */}
      <div
        style={{
          marginBottom: "25px",
        }}
      >

        <p
          style={{
            color: "#94a3b8",

            marginBottom: "12px",

            fontSize: "16px",

            fontWeight: "bold",
          }}
        >
          Questions rapides
        </p>

        <div
          style={{
            display: "flex",

            flexDirection: "column",

            gap: "10px",
          }}
        >

          <button
            onClick={() =>
              quickQuestion("inscription")
            }
            style={buttonStyle}
          >
            📚 Inscription
          </button>

          <button
            onClick={() =>
              quickQuestion("examens")
            }
            style={buttonStyle}
          >
            📝 Examens
          </button>

          <button
            onClick={() =>
              quickQuestion("calendrier")
            }
            style={buttonStyle}
          >
            📅 Calendrier
          </button>

        </div>

      </div>

      {/* CONVERSATIONS */}
      <div
        style={{
          flex: 1,
        }}
      >

        <p
          style={{
            color: "#94a3b8",

            marginBottom: "12px",

            fontSize: "16px",

            fontWeight: "bold",
          }}
        >
          Conversations
        </p>

        <div
          style={{
            display: "flex",

            flexDirection: "column",

            gap: "10px",
          }}
        >

          {conversations.map((conv) => (

            <div
              key={conv.id}

              style={{

                backgroundColor:

                  currentConversationId ===
                  conv.id

                    ? "#2563eb"

                    : "#1e293b",

                padding: "10px",

                borderRadius: "12px",

                cursor: "pointer",

                display: "flex",

                justifyContent:
                  "space-between",

                alignItems: "center",

                gap: "10px",
              }}
            >

              {/* SELECT CHAT */}
              <div
                onClick={() =>
                  selectConversation(
                    conv.id
                  )
                }
                style={{
                  flex: 1,

                  fontSize: "13px",

                  wordBreak: "break-word",
                }}
              >
                {conv.title}
              </div>

              {/* DELETE */}
              <button
                onClick={() =>
                  deleteConversation(
                    conv.id
                  )
                }
                style={{
                  background: "none",

                  border: "none",

                  color: "white",

                  cursor: "pointer",

                  fontSize: "14px",
                }}
              >
                ❌
              </button>

            </div>

          ))}

        </div>

      </div>

    </div>
  );
}

// STYLE BUTTONS
const buttonStyle = {

  backgroundColor: "#1e293b",

  border: "none",

  color: "white",

  padding: "12px",

  borderRadius: "12px",

  cursor: "pointer",

  fontSize: "14px",

};

export default Sidebar;