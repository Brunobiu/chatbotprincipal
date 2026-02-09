'use client';

import { useRouter } from 'next/navigation';

export default function TrialExpiredModal() {
  const router = useRouter();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full text-center">
        <div className="mb-6">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            🔒 Trial Expirado
          </h2>
          <p className="text-gray-600 text-lg">
            Seu período de teste terminou.
          </p>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-blue-900 font-medium">
            Assine agora para continuar usando todos os recursos!
          </p>
        </div>

        <button
          onClick={() => router.push('/planos')}
          className="w-full bg-blue-600 text-white py-4 rounded-lg font-semibold text-lg hover:bg-blue-700 transition"
        >
          Escolher Plano
        </button>

        <p className="text-sm text-gray-500 mt-4">
          Planos a partir de R$ 97/mês
        </p>
      </div>
    </div>
  );
}
