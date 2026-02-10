'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

export default function CTA() {
    return (
        <section className="relative py-12 overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-purple-900 to-blue-900" />

            {/* Animated circles */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-float" />
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-float-delayed" />

            {/* Grid pattern */}
            <div
                className="absolute inset-0 opacity-10"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                }}
            />

            <div className="container-custom relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center"
                >
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-xl sm:text-2xl lg:text-3xl font-bold text-white mb-3"
                    >
                        Teste gratuitamente agora
                    </motion.h2>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="text-sm text-blue-100 mb-4 max-w-2xl mx-auto"
                    >
                        Transforme mais conversas em vendas, leads e conversões hoje mesmo
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.3 }}
                        className="flex flex-col sm:flex-row gap-2.5 justify-center"
                    >
                        <button
                            onClick={() => {
                                window.scrollTo({ top: 0, behavior: 'smooth' });
                                setTimeout(() => {
                                    window.location.href = '/login';
                                }, 800);
                            }}
                            className="relative inline-flex items-center justify-center px-6 py-2.5 font-bold text-blue-900 text-xs
                             bg-white rounded-full overflow-hidden transition-all duration-300
                             hover:shadow-xl hover:shadow-white/25 group cursor-pointer"
                        >
                            <span className="relative z-10 flex items-center gap-1.5">
                                COMEÇAR GRÁTIS
                                <svg className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                                </svg>
                            </span>
                            <div className="absolute inset-0 bg-gradient-to-r from-blue-100 to-purple-100 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </button>

                        <a href="#como-funciona">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="inline-flex items-center justify-center px-6 py-2.5 font-bold text-white text-xs
                         border-2 border-white/30 rounded-full
                         hover:bg-white/10 transition-all duration-300"
                            >
                                Ver Demonstração
                            </motion.button>
                        </a>
                    </motion.div>

                    {/* Trust indicators */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.5 }}
                        className="mt-4 flex flex-wrap items-center justify-center gap-4 text-blue-200 text-xs"
                    >
                        <div className="flex items-center gap-1.5">
                            <svg className="w-3.5 h-3.5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span>Grátis por 7 dias</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <svg className="w-3.5 h-3.5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span>Sem cartão</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <svg className="w-3.5 h-3.5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span>Cancele quando quiser</span>
                        </div>
                    </motion.div>
                </motion.div>
            </div>
        </section>
    );
}
