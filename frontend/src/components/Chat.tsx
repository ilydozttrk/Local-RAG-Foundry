import {
  FileSearch,
  LoaderCircle,
  Send,
  Sparkles,
} from "lucide-react";
import {
  type FormEvent,
  type KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

import {
  askQuestion,
  type SourceResponse,
} from "../services/api";

interface ChatProps {
  selectedDocumentIds: number[];
}

interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources?: SourceResponse[];
}

function Chat({
  selectedDocumentIds,
}: ChatProps) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(
    [],
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(
    null,
  );

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageIdRef = useRef(0);

  const createMessageId = () => {
    messageIdRef.current += 1;

    return messageIdRef.current;
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading, error]);

  const sendQuestion = async (
    submittedQuestion: string,
  ) => {
    const cleanedQuestion = submittedQuestion.trim();

    if (!cleanedQuestion || loading) {
      return;
    }

    if (selectedDocumentIds.length === 0) {
      setError(
        "Please select at least one document before asking a question.",
      );

      return;
    }

    const userMessage: ChatMessage = {
      id: createMessageId(),
      role: "user",
      content: cleanedQuestion,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setQuestion("");
    setError(null);
    setLoading(true);

    try {
      const response = await askQuestion(
        cleanedQuestion,
        selectedDocumentIds,
      );

      const assistantMessage: ChatMessage = {
        id: createMessageId(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);
    } catch (requestError: unknown) {
      if (axios.isAxiosError(requestError)) {
        const detail =
          requestError.response?.data?.detail;

        if (typeof detail === "string") {
          setError(detail);
        } else {
          setError(
            "The assistant could not generate an answer.",
          );
        }
      } else {
        setError(
          "An unexpected error occurred while generating the answer.",
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    void sendQuestion(question);
  };

  const handleKeyDown = (
    event: KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      void sendQuestion(question);
    }
  };

  const handleQuestionChange = (
    value: string,
  ) => {
    setQuestion(value);

    if (error) {
      setError(null);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setQuestion("");
    setError(null);
  };

  const handleSuggestion = (
    suggestedQuestion: string,
  ) => {
    setQuestion(suggestedQuestion);
    setError(null);
  };

  const hasMessages = messages.length > 0;
  const hasSelectedDocuments =
    selectedDocumentIds.length > 0;

  return (
    <main className="chat">
      <div className="chat-toolbar">
        <div>
          <span className="section-label">
            Conversation
          </span>

          <h2>Chat with your documents</h2>
        </div>

        <button
          className="clear-button"
          type="button"
          onClick={handleClearChat}
          disabled={!hasMessages && !error}
        >
          Clear chat
        </button>
      </div>

      <section
        className={`messages ${
          hasMessages ? "messages-active" : ""
        }`}
        aria-live="polite"
      >
        {!hasMessages && (
          <>
            <div className="welcome-card">
              <div className="welcome-icon">
                <Sparkles
                  size={28}
                  aria-hidden="true"
                />
              </div>

              <div className="welcome-copy">
                <span className="eyebrow">
                  Local intelligence
                </span>

                <h3>
                  Ask questions grounded in your own files.
                </h3>

                <p>
                  Upload one or more documents, select the
                  files you want to use, then ask a question.
                  Answers will be generated locally using
                  retrieved context from your knowledge base.
                </p>
              </div>
            </div>

            <div className="suggestion-grid">
              <button
                className="suggestion-card"
                type="button"
                onClick={() =>
                  handleSuggestion(
                    "Summarize the main ideas in the selected documents.",
                  )
                }
              >
                <FileSearch
                  size={18}
                  aria-hidden="true"
                />

                <span>
                  <strong>
                    Summarize selected documents
                  </strong>
                  Get a concise overview of the selected
                  content.
                </span>
              </button>

              <button
                className="suggestion-card"
                type="button"
                onClick={() =>
                  handleSuggestion(
                    "What are the most important findings in the selected documents?",
                  )
                }
              >
                <Sparkles
                  size={18}
                  aria-hidden="true"
                />

                <span>
                  <strong>
                    Ask a focused question
                  </strong>
                  Retrieve relevant passages before
                  generating an answer.
                </span>
              </button>
            </div>
          </>
        )}

        {messages.map((message) => (
          <article
            key={message.id}
            className={
              `chat-message ` +
              `chat-message-${message.role}`
            }
          >
            <div className="message-role">
              {message.role === "user"
                ? "You"
                : "Local RAG"}
            </div>

            <div className="message-content">
              {message.role === "assistant" ? (
                <ReactMarkdown>
                  {message.content}
                </ReactMarkdown>
              ) : (
                <p>{message.content}</p>
              )}
            </div>

            {message.role === "assistant" &&
              message.sources &&
              message.sources.length > 0 && (
                <div className="message-sources">
                  <span className="sources-heading">
                    Retrieved sources
                  </span>

                  {message.sources.map(
                    (source, sourceIndex) => (
                      <details
                        key={
                          `${source.chunk_id}-` +
                          `${sourceIndex}`
                        }
                        className="source-card"
                      >
                        <summary>
                          <span>
                            {source.filename ??
                              `Document ${source.document_id}`}
                          </span>

                          <span>
                            {(
                              source.similarity_score *
                              100
                            ).toFixed(1)}
                            %
                          </span>
                        </summary>

                        <div className="source-details">
                          {source.chunk_index !==
                            null &&
                            source.chunk_index !==
                              undefined && (
                              <span>
                                Chunk{" "}
                                {source.chunk_index}
                              </span>
                            )}

                          {source.source_path && (
                            <span>
                              {source.source_path}
                            </span>
                          )}

                          {source.content && (
                            <p>{source.content}</p>
                          )}
                        </div>
                      </details>
                    ),
                  )}
                </div>
              )}
          </article>
        ))}

        {loading && (
          <article className="chat-message chat-message-assistant">
            <div className="message-role">
              Local RAG
            </div>

            <div
              className="message-loading"
              role="status"
            >
              <LoaderCircle
                className="message-spinner"
                size={18}
                aria-hidden="true"
              />

              <span>
                Retrieving context and generating an
                answer...
              </span>
            </div>
          </article>
        )}

        {error && (
          <div
            className="chat-error"
            role="alert"
          >
            <strong>Request failed</strong>
            <span>{error}</span>
          </div>
        )}

        <div
          ref={messagesEndRef}
          aria-hidden="true"
        />
      </section>

      <form
        className="composer-wrapper"
        onSubmit={handleSubmit}
      >
        <div className="composer">
          <textarea
            rows={1}
            value={question}
            onChange={(event) =>
              handleQuestionChange(
                event.target.value,
              )
            }
            onKeyDown={handleKeyDown}
            placeholder={
              hasSelectedDocuments
                ? "Ask anything about the selected documents..."
                : "Select at least one document to begin..."
            }
            aria-label="Message"
            disabled={loading}
          />

          <button
            className="send-button"
            type="submit"
            aria-label="Send message"
            disabled={
              !question.trim() ||
              loading ||
              !hasSelectedDocuments
            }
          >
            {loading ? (
              <LoaderCircle
                className="message-spinner"
                size={19}
                aria-hidden="true"
              />
            ) : (
              <Send
                size={19}
                aria-hidden="true"
              />
            )}
          </button>
        </div>

        <p className="composer-note">
          {hasSelectedDocuments
            ? `${selectedDocumentIds.length} ${
                selectedDocumentIds.length === 1
                  ? "document"
                  : "documents"
              } selected. Answers are generated locally.`
            : "Select at least one document before asking a question."}
        </p>
      </form>
    </main>
  );
}

export default Chat;