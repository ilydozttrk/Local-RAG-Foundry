import {
  Bot,
  CheckCircle2,
  Database,
  FileText,
  HardDrive,
  LoaderCircle,
  UploadCloud,
  XCircle,
} from "lucide-react";
import {
  type ChangeEvent,
  useRef,
  useState,
} from "react";
import axios from "axios";

import {
  type UploadResponse,
  uploadDocument,
} from "../services/api";

function Sidebar() {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] =
    useState<UploadResponse | null>(null);
  const [uploadError, setUploadError] =
    useState<string | null>(null);

  const handleUploadClick = () => {
    if (uploading) {
      return;
    }

    fileInputRef.current?.click();
  };

  const handleFileChange = async (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    setUploading(true);
    setUploadResult(null);
    setUploadError(null);

    try {
      const result = await uploadDocument(selectedFile);

      setUploadResult(result);
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;

        if (typeof detail === "string") {
          setUploadError(detail);
        } else {
          setUploadError(
            "The document could not be uploaded.",
          );
        }
      } else {
        setUploadError(
          "An unexpected error occurred during upload.",
        );
      }
    } finally {
      setUploading(false);

      /*
       * Reset the input so the same file can be selected again.
       */
      event.target.value = "";
    }
  };

  const documentCount =
    uploadResult?.status === "success" ? 1 : 0;

  return (
    <aside className="sidebar">
      <section className="sidebar-section">
        <div className="section-heading">
          <div>
            <span className="section-label">Workspace</span>
            <h2>Knowledge Base</h2>
          </div>

          <span className="document-count">
            {documentCount}
          </span>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,application/pdf,text/plain"
          onChange={handleFileChange}
          disabled={uploading}
          style={{ display: "none" }}
        />

        <button
          className="upload-card"
          type="button"
          onClick={handleUploadClick}
          disabled={uploading}
        >
          <span className="upload-icon-wrapper">
            {uploading ? (
              <LoaderCircle
                className="upload-spinner"
                size={24}
              />
            ) : (
              <UploadCloud size={24} />
            )}
          </span>

          <strong>
            {uploading
              ? "Processing document..."
              : "Upload documents"}
          </strong>

          <span>
            {uploading
              ? "Creating chunks and embeddings"
              : "PDF or TXT files"}
          </span>
        </button>

        {uploadResult && (
          <div
            className={`upload-feedback upload-feedback-${uploadResult.status}`}
          >
            {uploadResult.status === "success" ? (
              <CheckCircle2 size={17} />
            ) : (
              <FileText size={17} />
            )}

            <div>
              <strong>
                {uploadResult.status === "success"
                  ? "Upload completed"
                  : "Document skipped"}
              </strong>

              <span>{uploadResult.message}</span>
            </div>
          </div>
        )}

        {uploadError && (
          <div className="upload-feedback upload-feedback-error">
            <XCircle size={17} />

            <div>
              <strong>Upload failed</strong>
              <span>{uploadError}</span>
            </div>
          </div>
        )}
      </section>

      <section className="sidebar-section documents-section">
        <div className="list-heading">
          <FileText size={15} />
          <span>Documents</span>
        </div>

        {uploadResult?.status === "success" ? (
          <div className="uploaded-document">
            <div className="uploaded-document-icon">
              <FileText size={18} />
            </div>

            <div className="uploaded-document-details">
              <strong title={uploadResult.filename}>
                {uploadResult.filename}
              </strong>

              <span>
                {uploadResult.chunk_count} chunks ·{" "}
                {uploadResult.embedding_count} embeddings
              </span>
            </div>
          </div>
        ) : (
          <div className="empty-documents">
            <div className="empty-document-icon">
              <HardDrive size={20} />
            </div>

            <p>No documents yet</p>

            <span>
              Upload a file to begin building your local
              knowledge base.
            </span>
          </div>
        )}
      </section>

      <section className="system-card">
        <div className="system-card-heading">
          <span>Local services</span>
          <span className="online-label">Online</span>
        </div>

        <div className="service-row">
          <div className="service-name">
            <Bot size={16} />
            <span>Foundry Local</span>
          </div>

          <span className="service-status-dot" />
        </div>

        <div className="service-row">
          <div className="service-name">
            <Database size={16} />
            <span>Vector Database</span>
          </div>

          <span className="service-status-dot" />
        </div>
      </section>
    </aside>
  );
}

export default Sidebar;