import { FileSearch, Send, Sparkles } from "lucide-react";

function Chat() {
  return (
    <main className="chat">
      <div className="chat-toolbar">
        <div>
          <span className="section-label">Conversation</span>
          <h2>Chat with your documents</h2>
        </div>

        <button className="clear-button" type="button">
          Clear chat
        </button>
      </div>

      <section className="messages">
        <div className="welcome-card">
          <div className="welcome-icon">
            <Sparkles size={28} />
          </div>

          <div className="welcome-copy">
            <span className="eyebrow">Local intelligence</span>
            <h3>Ask questions grounded in your own files.</h3>

            <p>
              Upload one or more documents, then ask a question. Answers will be
              generated locally using retrieved context from your knowledge
              base.
            </p>
          </div>
        </div>

        <div className="suggestion-grid">
          <button className="suggestion-card" type="button">
            <FileSearch size={18} />

            <span>
              <strong>Summarize a document</strong>
              Get a concise overview of the uploaded content.
            </span>
          </button>

          <button className="suggestion-card" type="button">
            <Sparkles size={18} />

            <span>
              <strong>Ask a focused question</strong>
              Retrieve relevant passages before generating an answer.
            </span>
          </button>
        </div>
      </section>

      <div className="composer-wrapper">
        <div className="composer">
          <textarea
            rows={1}
            placeholder="Ask anything about your documents..."
            aria-label="Message"
          />

          <button className="send-button" type="button" aria-label="Send">
            <Send size={19} />
          </button>
        </div>

        <p className="composer-note">
          Answers are generated locally and may require document verification.
        </p>
      </div>
    </main>
  );
}

export default Chat;