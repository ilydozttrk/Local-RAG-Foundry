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
  useMemo,
  useRef,
  useState,
} from "react";
import axios from "axios";

import {
  type UploadResponse,
  uploadDocument,
} from "../services/api";

interface DocumentItem {
  document_id: number;
  filename: string;
  file_type: string;
  chunk_count: number;
  embedding_count: number;
  is_active: boolean;
}

interface SidebarProps {
  documents: DocumentItem[];
  selectedDocumentIds: number[];
  documentsLoading: boolean;
  documentsError: string | null;
  onSelectionChange: (
    documentIds: number[],
  ) => void;
  onDocumentsChanged: (
    newlyUploadedDocumentId?: number,
  ) => Promise<void>;
}

function formatFileType(fileType: string): string {
  const normalizedFileType = fileType
    .replace(".", "")
    .trim()
    .toUpperCase();

  return normalizedFileType || "FILE";
}

function Sidebar({
  documents,
  selectedDocumentIds,
  documentsLoading,
  documentsError,
  onSelectionChange,
  onDocumentsChanged,
}: SidebarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] =
    useState<UploadResponse | null>(null);
  const [uploadError, setUploadError] =
    useState<string | null>(null);

  const activeDocuments = useMemo(
    () =>
      documents.filter(
        (document) => document.is_active,
      ),
    [documents],
  );

  const selectedDocumentIdSet = useMemo(
    () => new Set(selectedDocumentIds),
    [selectedDocumentIds],
  );

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

      /*
       * Refresh the document list after the upload request.
       * App.tsx automatically selects a successfully indexed
       * document using the returned document ID.
       */
      await onDocumentsChanged(
        result.document_id ?? undefined,
      );
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

  const handleDocumentSelection = (
    documentId: number,
  ) => {
    const isSelected =
      selectedDocumentIdSet.has(documentId);

    if (isSelected) {
      onSelectionChange(
        selectedDocumentIds.filter(
          (selectedId) =>
            selectedId !== documentId,
        ),
      );

      return;
    }

    onSelectionChange([
      ...selectedDocumentIds,
      documentId,
    ]);
  };

  const handleSelectAll = () => {
    onSelectionChange(
      activeDocuments.map(
        (document) => document.document_id,
      ),
    );
  };

  const handleClearSelection = () => {
    onSelectionChange([]);
  };

  const allActiveDocumentsSelected =
    activeDocuments.length > 0 &&
    activeDocuments.every((document) =>
      selectedDocumentIdSet.has(
        document.document_id,
      ),
    );

  return (
    <aside
      className="sidebar"
      aria-label="Knowledge base sidebar"
    >
      <section className="sidebar-section">
        <div className="section-heading">
          <div>
            <span className="section-label">
              Workspace
            </span>

            <h2>Knowledge Base</h2>
          </div>

          <span
            className="document-count"
            title={`${activeDocuments.length} active documents`}
          >
            {activeDocuments.length}
          </span>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,application/pdf,text/plain"
          onChange={handleFileChange}
          disabled={uploading}
          aria-label="Choose a PDF or TXT document"
          style={{ display: "none" }}
        />

        <button
          className="upload-card"
          type="button"
          onClick={handleUploadClick}
          disabled={uploading}
          aria-busy={uploading}
        >
          <span className="upload-icon-wrapper">
            {uploading ? (
              <LoaderCircle
                className="upload-spinner"
                size={24}
                aria-hidden="true"
              />
            ) : (
              <UploadCloud
                size={24}
                aria-hidden="true"
              />
            )}
          </span>

          <strong>
            {uploading
              ? "Indexing document..."
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
            className={
              `upload-feedback ` +
              `upload-feedback-${uploadResult.status}`
            }
            role="status"
          >
            {uploadResult.status === "success" ? (
              <CheckCircle2
                size={17}
                aria-hidden="true"
              />
            ) : uploadResult.status === "failed" ? (
              <XCircle
                size={17}
                aria-hidden="true"
              />
            ) : (
              <FileText
                size={17}
                aria-hidden="true"
              />
            )}

            <div>
              <strong>
                {uploadResult.status === "success"
                  ? "Document indexed"
                  : uploadResult.status === "failed"
                    ? "Indexing failed"
                    : "Document skipped"}
              </strong>

              <span>{uploadResult.message}</span>
            </div>
          </div>
        )}

        {uploadError && (
          <div
            className="upload-feedback upload-feedback-error"
            role="alert"
          >
            <XCircle
              size={17}
              aria-hidden="true"
            />

            <div>
              <strong>Upload failed</strong>
              <span>{uploadError}</span>
            </div>
          </div>
        )}
      </section>

      <section className="sidebar-section documents-section">
        <div className="list-heading">
          <div className="service-name">
            <FileText
              size={15}
              aria-hidden="true"
            />
            <span>Documents</span>
          </div>

          {activeDocuments.length > 0 && (
            <button
              className="clear-button"
              type="button"
              onClick={
                allActiveDocumentsSelected
                  ? handleClearSelection
                  : handleSelectAll
              }
            >
              {allActiveDocumentsSelected
                ? "Clear"
                : "Select all"}
            </button>
          )}
        </div>

        {documentsLoading ? (
          <div
            className="empty-documents"
            role="status"
          >
            <div className="empty-document-icon">
              <LoaderCircle
                className="upload-spinner"
                size={20}
                aria-hidden="true"
              />
            </div>

            <p>Loading documents</p>

            <span>
              Reading the local knowledge base.
            </span>
          </div>
        ) : documentsError ? (
          <div
            className="upload-feedback upload-feedback-error"
            role="alert"
          >
            <XCircle
              size={17}
              aria-hidden="true"
            />

            <div>
              <strong>Documents unavailable</strong>
              <span>{documentsError}</span>
            </div>
          </div>
        ) : activeDocuments.length > 0 ? (
          <div className="documents-list">
            {activeDocuments.map((document) => {
              const isSelected =
                selectedDocumentIdSet.has(
                  document.document_id,
                );

              const formattedFileType =
                formatFileType(document.file_type);

              return (
                <label
                  className="uploaded-document"
                  key={document.document_id}
                  title={
                    isSelected
                      ? `Deselect ${document.filename}`
                      : `Select ${document.filename}`
                  }
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() =>
                      handleDocumentSelection(
                        document.document_id,
                      )
                    }
                    aria-label={`Select ${document.filename}`}
                  />

                  <div className="uploaded-document-icon">
                    <FileText
                      size={18}
                      aria-hidden="true"
                    />
                  </div>

                  <div className="uploaded-document-details">
                    <strong title={document.filename}>
                      {document.filename}
                    </strong>

                    <span>
                      {formattedFileType} •{" "}
                      {document.chunk_count}{" "}
                      {document.chunk_count === 1
                        ? "chunk"
                        : "chunks"}
                    </span>
                  </div>

                  {isSelected && (
                    <CheckCircle2
                      className="selected-document-icon"
                      size={17}
                      aria-hidden="true"
                    />
                  )}
                </label>
              );
            })}
          </div>
        ) : (
          <div className="empty-documents">
            <div className="empty-document-icon">
              <HardDrive
                size={20}
                aria-hidden="true"
              />
            </div>

            <p>No documents yet</p>

            <span>
              Upload a file to begin building your
              local knowledge base.
            </span>
          </div>
        )}
      </section>

      <section className="system-card">
        <div className="system-card-heading">
          <span>Local services</span>
          <span className="online-label">
            Online
          </span>
        </div>

        <div className="service-row">
          <div className="service-name">
            <Bot
              size={16}
              aria-hidden="true"
            />
            <span>Foundry Local</span>
          </div>

          <span
            className="service-status-dot"
            aria-label="Foundry Local is online"
          />
        </div>

        <div className="service-row">
          <div className="service-name">
            <Database
              size={16}
              aria-hidden="true"
            />
            <span>Vector Database</span>
          </div>

          <span
            className="service-status-dot"
            aria-label="Vector database is online"
          />
        </div>
      </section>
    </aside>
  );
}

export default Sidebar;