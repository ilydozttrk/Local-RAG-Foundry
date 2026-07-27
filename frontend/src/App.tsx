import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import axios from "axios";

import "./styles/app.css";

import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Chat from "./components/Chat";
import api from "./services/api";


export interface DocumentItem {
  document_id: number;
  filename: string;
  file_type: string;
  chunk_count: number;
  embedding_count: number;
  is_active: boolean;
}


function App() {
  const documentSelectionInitialized = useRef(false);

  const [documents, setDocuments] = useState<DocumentItem[]>(
    [],
  );

  const [
    selectedDocumentIds,
    setSelectedDocumentIds,
  ] = useState<number[]>([]);

  const [
    documentsLoading,
    setDocumentsLoading,
  ] = useState(true);

  const [
    documentsError,
    setDocumentsError,
  ] = useState<string | null>(null);

  const refreshDocuments = useCallback(
    async (
      newlyUploadedDocumentId?: number,
    ): Promise<void> => {
      setDocumentsLoading(true);
      setDocumentsError(null);

      try {
        const response = await api.get<DocumentItem[]>(
          "/api/documents",
        );

        const fetchedDocuments = response.data;
        const activeDocuments = fetchedDocuments.filter(
          (document) => document.is_active,
        );

        const activeDocumentIds = activeDocuments.map(
          (document) => document.document_id,
        );

        setDocuments(fetchedDocuments);

        setSelectedDocumentIds(
          (currentSelectedDocumentIds) => {
            /*
             * On the initial page load, select every active
             * document automatically.
             */
            if (!documentSelectionInitialized.current) {
              documentSelectionInitialized.current = true;

              return activeDocumentIds;
            }

            /*
             * After later refreshes, preserve valid selections
             * and remove documents that are no longer active.
             */
            const nextSelectedDocumentIds =
              currentSelectedDocumentIds.filter(
                (documentId) =>
                  activeDocumentIds.includes(documentId),
              );

            /*
             * Automatically select a successfully uploaded
             * document so it can immediately be used in chat.
             */
            if (
              newlyUploadedDocumentId !== undefined &&
              activeDocumentIds.includes(
                newlyUploadedDocumentId,
              ) &&
              !nextSelectedDocumentIds.includes(
                newlyUploadedDocumentId,
              )
            ) {
              nextSelectedDocumentIds.push(
                newlyUploadedDocumentId,
              );
            }

            return nextSelectedDocumentIds;
          },
        );
      } catch (error: unknown) {
        if (axios.isAxiosError(error)) {
          const detail = error.response?.data?.detail;

          if (typeof detail === "string") {
            setDocumentsError(detail);
          } else {
            setDocumentsError(
              "The document list could not be loaded.",
            );
          }
        } else {
          setDocumentsError(
            "An unexpected error occurred while loading documents.",
          );
        }
      } finally {
        setDocumentsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    void refreshDocuments();
  }, [refreshDocuments]);

  return (
    <div className="app">
      <Header />

      <div className="content">
        <Sidebar
          documents={documents}
          selectedDocumentIds={selectedDocumentIds}
          documentsLoading={documentsLoading}
          documentsError={documentsError}
          onSelectionChange={setSelectedDocumentIds}
          onDocumentsChanged={refreshDocuments}
        />

        <Chat
          selectedDocumentIds={selectedDocumentIds}
        />
      </div>
    </div>
  );
}

export default App;