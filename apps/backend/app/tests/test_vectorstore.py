"""
Testes para Vectorstore Multi-tenant
"""
import pytest
from unittest.mock import patch, MagicMock

from app.services.rag.vectorstore import (
    get_collection_name,
    criar_vectorstore_cliente,
    deletar_vectorstore_cliente
)


@pytest.mark.unit
class TestVectorstoreMultiTenant:
    """Testes unitários para isolamento multi-tenant no vectorstore"""
    
    def test_get_collection_name(self):
        """Testa geração de nome de coleção por cliente"""
        assert get_collection_name(1) == "tenant_1"
        assert get_collection_name(2) == "tenant_2"
        assert get_collection_name(999) == "tenant_999"
    
    def test_collection_names_diferentes(self):
        """Testa que clientes diferentes têm coleções diferentes"""
        collection_1 = get_collection_name(1)
        collection_2 = get_collection_name(2)
        
        assert collection_1 != collection_2
        assert "tenant_" in collection_1
        assert "tenant_" in collection_2
    
    @patch('app.services.rag.vectorstore.Chroma')
    @patch('app.services.rag.vectorstore.OpenAIEmbeddings')
    def test_criar_vectorstore_cliente(self, mock_embeddings, mock_chroma):
        """Testa criação de vectorstore isolado por cliente"""
        # Mock do Chroma
        mock_vectorstore = MagicMock()
        mock_chroma.from_documents.return_value = mock_vectorstore
        
        # Criar vectorstore para cliente 1
        documentos = ["Documento 1 do cliente 1", "Documento 2 do cliente 1"]
        vectorstore = criar_vectorstore_cliente(1, documentos)
        
        # Verificar que foi chamado com collection_name correto
        mock_chroma.from_documents.assert_called_once()
        call_kwargs = mock_chroma.from_documents.call_args[1]
        assert call_kwargs['collection_name'] == "tenant_1"
        
        # Verificar que retornou o vectorstore
        assert vectorstore == mock_vectorstore
    
    @patch('app.services.rag.vectorstore.Chroma')
    @patch('app.services.rag.vectorstore.OpenAIEmbeddings')
    def test_criar_vectorstore_clientes_diferentes(self, mock_embeddings, mock_chroma):
        """Testa que clientes diferentes criam coleções isoladas"""
        mock_vectorstore = MagicMock()
        mock_chroma.from_documents.return_value = mock_vectorstore
        
        # Cliente 1
        documentos_1 = ["Produto X custa R$ 100"]
        criar_vectorstore_cliente(1, documentos_1)
        call_1 = mock_chroma.from_documents.call_args[1]
        
        # Cliente 2
        documentos_2 = ["Produto Y custa R$ 200"]
        criar_vectorstore_cliente(2, documentos_2)
        call_2 = mock_chroma.from_documents.call_args[1]
        
        # Verificar que usaram coleções diferentes
        assert call_1['collection_name'] == "tenant_1"
        assert call_2['collection_name'] == "tenant_2"
        assert call_1['collection_name'] != call_2['collection_name']
    
    @patch('app.services.rag.vectorstore.Chroma')
    @patch('app.services.rag.vectorstore.OpenAIEmbeddings')
    def test_deletar_vectorstore_cliente(self, mock_embeddings, mock_chroma):
        """Testa deleção de vectorstore de um cliente"""
        # Mock do Chroma
        mock_vectorstore = MagicMock()
        mock_chroma.return_value = mock_vectorstore
        
        # Deletar vectorstore do cliente 1
        deletar_vectorstore_cliente(1)
        
        # Verificar que foi criado com collection_name correto
        mock_chroma.assert_called_once()
        call_kwargs = mock_chroma.call_args[1]
        assert call_kwargs['collection_name'] == "tenant_1"
        
        # Verificar que delete_collection foi chamado
        mock_vectorstore.delete_collection.assert_called_once()
    
    @patch('app.services.rag.vectorstore.RecursiveCharacterTextSplitter')
    @patch('app.services.rag.vectorstore.Chroma')
    @patch('app.services.rag.vectorstore.OpenAIEmbeddings')
    def test_chunk_size_e_overlap(self, mock_embeddings, mock_chroma, mock_splitter):
        """Testa que chunk size e overlap estão configurados corretamente"""
        mock_vectorstore = MagicMock()
        mock_chroma.from_documents.return_value = mock_vectorstore
        
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.split_documents.return_value = []
        mock_splitter.return_value = mock_splitter_instance
        
        # Criar vectorstore
        documentos = ["Documento teste"]
        criar_vectorstore_cliente(1, documentos)
        
        # Verificar configuração do splitter
        mock_splitter.assert_called_once_with(
            chunk_size=800,
            chunk_overlap=160
        )
