import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import "./styles/app.css";

import Chat from "./components/Chat";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import api, {
  getApiErrorMessage,
} from "./services/api";

export interface DocumentItem {
  document_id: number;
  filename: string;
  file_type: string;
  chunk_count: number;
  embedding_count: number;
  is_active: boolean;
}

function areNumberArraysEqual(
  first: number[],
  second: number[],
): boolean {
  return (
    first.length === second.length &&
    first.every(
      (value, index) => value === second[index],
    )
  );
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

        const activeDocumentIds = fetchedDocuments
          .filter((document) => document.is_active)
          .map((document) => document.document_id);

        const activeDocumentIdSet = new Set(
          activeDocumentIds,
        );

        setDocuments(fetchedDocuments);

        setSelectedDocumentIds(
          (currentSelectedDocumentIds) => {
            if (!documentSelectionInitialized.current) {
              documentSelectionInitialized.current = true;

              return activeDocumentIds;
            }

            const nextSelectedDocumentIds =
              currentSelectedDocumentIds.filter(
                (documentId) =>
                  activeDocumentIdSet.has(documentId),
              );

            if (
              newlyUploadedDocumentId !== undefined &&
              activeDocumentIdSet.has(
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

            if (
              areNumberArraysEqual(
                currentSelectedDocumentIds,
                nextSelectedDocumentIds,
              )
            ) {
              return currentSelectedDocumentIds;
            }

            return nextSelectedDocumentIds;
          },
        );
      } catch (error: unknown) {
        setDocumentsError(
          getApiErrorMessage(
            error,
            "The document list could not be loaded.",
          ),
        );
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

      <main className="content">
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
      </main>
    </div>
  );
}

export default App;