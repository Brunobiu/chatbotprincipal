'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.15,
            delayChildren: 0.3,
        },
    },
};

const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.6, ease: 'easeOut' },
    },
};

const bubbleVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: (i: number) => ({
        opacity: 1,
        scale: 1,
        transition: {
            delay: 0.8 + i * 0.2,
            duration: 0.5,
            ease: 'easeOut',
        },
    }),
};

const chatBubbles = [
    { text: 'Olá! Como posso ajudar?', isBot: true, delay: 0 },
    { text: 'Quero saber mais sobre automação', isBot: false, delay: 1 },
    { text: 'Claro! Posso te enviar um guia completo 📚', isBot: true, delay: 2 },
    { text: 'Sim, por favor!', isBot: false, delay: 3 },
];

export default function Hero() {
    return (
        <section className="relative min-h-screen flex items-center overflow-hidden pt-20">
            {/* Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50" />

            {/* Animated circles */}
            <div className="absolute top-20 right-10 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl animate-float" />
            <div className="absolute bottom-20 left-10 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl animate-float-delayed" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-300/10 rounded-full blur-3xl" />

            <div className="container-custom relative z-10">
                <div className="grid lg:grid-cols-2 gap-12 items-center">
                    {/* Content */}
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        className="text-center lg:text-left"
                    >
                        <motion.div
                            variants={itemVariants}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 rounded-full text-blue-700 text-sm font-medium mb-6"
                        >
                            <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                            Automação Inteligente com IA
                        </motion.div>

                        <motion.h1
                            variants={itemVariants}
                            className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6"
                        >
                            Transforme cada{' '}
                            <span className="text-gradient">conversa</span> em uma{' '}
                            <span className="text-gradient">oportunidade</span>
                        </motion.h1>

                        <motion.p
                            variants={itemVariants}
                            className="text-lg sm:text-xl text-gray-600 mb-8 max-w-lg mx-auto lg:mx-0"
                        >
                            Venda mais, aumente seu engajamento e ganhe mais seguidores com
                            automações inteligentes para Instagram, WhatsApp, TikTok e Messenger.
                        </motion.p>

                        <motion.div
                            variants={itemVariants}
                            className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
                        >
                            <Link href="/checkout">
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    className="btn-primary text-lg"
                                >
                                    <span>Teste Grátis Agora!</span>
                                </motion.button>
                            </Link>
                            <a href="#como-funciona">
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    className="btn-secondary text-lg"
                                >
                                    Ver Demonstração
                                </motion.button>
                            </a>
                        </motion.div>

                        {/* Trust badges */}
                        <motion.div
                            variants={itemVariants}
                            className="mt-10 flex items-center gap-6 justify-center lg:justify-start"
                        >
                            <div className="flex items-center gap-2">
                                <div className="flex -space-x-2">
                                    {[1, 2, 3, 4].map((i) => (
                                        <div
                                            key={i}
                                            className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 border-2 border-white"
                                        />
                                    ))}
                                </div>
                                <span className="text-sm text-gray-600">
                                    +1M empresas confiam
                                </span>
                            </div>
                            <div className="h-8 w-px bg-gray-300" />
                            <div className="flex items-center gap-1">
                                {[1, 2, 3, 4, 5].map((i) => (
                                    <svg key={i} className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                    </svg>
                                ))}
                                <span className="text-sm text-gray-600 ml-1">4.9/5</span>
                            </div>
                        </motion.div>
                    </motion.div>

                    {/* Phone Mockup */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 50 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.5, ease: 'easeOut' }}
                        className="relative flex justify-center"
                    >
                        <div className="relative w-[300px] sm:w-[340px]">
                            {/* Phone frame */}
                            <div className="relative bg-gray-900 rounded-[3rem] p-3 shadow-2xl shadow-blue-500/20">
                                <div className="bg-white rounded-[2.5rem] overflow-hidden">
                                    {/* Phone header */}
                                    <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                                                </svg>
                                            </div>
                                            <div>
                                                <p className="font-semibold">IA Bot</p>
                                                <p className="text-xs opacity-80">Online agora</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Chat area */}
                                    <div className="p-4 h-[400px] bg-gray-50 space-y-4 overflow-hidden">
                                        {chatBubbles.map((bubble, index) => (
                                            <motion.div
                                                key={index}
                                                custom={index}
                                                variants={bubbleVariants}
                                                initial="hidden"
                                                animate="visible"
                                                className={`flex ${bubble.isBot ? 'justify-start' : 'justify-end'}`}
                                            >
                                                <div
                                                    className={`max-w-[80%] p-3 rounded-2xl ${bubble.isBot
                                                            ? 'bg-white shadow-md rounded-bl-none'
                                                            : 'bg-blue-600 text-white rounded-br-none'
                                                        }`}
                                                >
                                                    {bubble.isBot && (
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <div className="w-5 h-5 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full" />
                                                            <span className="text-xs font-medium text-blue-600">IA Bot</span>
                                                        </div>
                                                    )}
                                                    <p className="text-sm">{bubble.text}</p>
                                                </div>
                                            </motion.div>
                                        ))}

                                        {/* Typing indicator */}
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: 2.5 }}
                                            className="flex justify-start"
                                        >
                                            <div className="bg-white shadow-md p-3 rounded-2xl rounded-bl-none">
                                                <div className="flex gap-1">
                                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                                </div>
                                            </div>
                                        </motion.div>
                                    </div>
                                </div>
                            </div>

                            {/* Floating elements */}
                            <motion.div
                                animate={{ y: [-10, 10, -10] }}
                                transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
                                className="absolute -left-16 top-20 bg-white p-3 rounded-xl shadow-lg"
                            >
                                <div className="flex items-center gap-2">
                                    <span className="text-2xl">📈</span>
                                    <div>
                                        <p className="text-xs text-gray-500">Conversões</p>
                                        <p className="font-bold text-green-600">+90%</p>
                                    </div>
                                </div>
                            </motion.div>

                            <motion.div
                                animate={{ y: [10, -10, 10] }}
                                transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
                                className="absolute -right-12 bottom-32 bg-white p-3 rounded-xl shadow-lg"
                            >
                                <div className="flex items-center gap-2">
                                    <span className="text-2xl">⏱️</span>
                                    <div>
                                        <p className="text-xs text-gray-500">Tempo de resposta</p>
                                        <p className="font-bold text-blue-600">Instantâneo</p>
                                    </div>
                                </div>
                            </motion.div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
