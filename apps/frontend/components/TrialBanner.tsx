'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface TrialStatus {
  subscription_status: string;
  trial_ends_at: string | null;
  days_remaining: number | null;
  is_expired: boolean;
}

export default function TrialBanner() {
  const [trialStatus, setTrialStatus] = useState<TrialStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrialStatus();
  }, []);

  const fetchTrialStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const res = await fetch('http://localhost:8000/api/v1/auth/trial-status', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (res.ok) {
        const data = await res.json();
        setTrialStatus(data);
      }
    } catch (error) {
      console.error('Erro ao buscar status do trial:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !trialStatus) return null;

  // Não mostrar se não estiver em trial
  if (trialStatus.subscription_status !== 'trial') return null;

  // Trial expirado
  if (trialStatus.is_expired) {
    return (
      <div className="bg-red-600 text-white px-6 py-4 rounded-lg shadow-lg mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="font-semibold text-lg">Trial Expirado</p>
              <p className="text-sm opacity-90">Seu período de teste terminou. Assine agora para continuar usando!</p>
            </div>
          </div>
          <Link
            href="/planos"
            className="bg-white text-red-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100 transition whitespace-nowrap"
          >
            Escolher Plano
          </Link>
        </div>
      </div>
    );
  }

  // Últimos 2 dias (urgência)
  if (trialStatus.days_remaining !== null && trialStatus.days_remaining <= 2) {
    return (
      <div className="bg-orange-500 text-white px-6 py-4 rounded-lg shadow-lg mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="font-semibold text-lg">⚠️ Trial Expirando - Resta{trialStatus.days_remaining === 1 ? '' : 'm'} {trialStatus.days_remaining} dia{trialStatus.days_remaining === 1 ? '' : 's'}</p>
              <p className="text-sm opacity-90">Não perca o acesso! Assine agora.</p>
            </div>
          </div>
          <Link
            href="/planos"
            className="bg-white text-orange-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100 transition whitespace-nowrap"
          >
            Assinar Agora
          </Link>
        </div>
      </div>
    );
  }

  // Trial normal
  return (
    <div className="bg-blue-600 text-white px-6 py-4 rounded-lg shadow-lg mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="font-semibold text-lg">⏰ Trial Gratuito - Restam {trialStatus.days_remaining} dias</p>
            <p className="text-sm opacity-90">Aproveite todos os recursos! Assine agora e ganhe 10% de desconto.</p>
          </div>
        </div>
        <Link
          href="/planos"
          className="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100 transition whitespace-nowrap"
        >
          Assinar Agora
        </Link>
      </div>
    </div>
  );
}
