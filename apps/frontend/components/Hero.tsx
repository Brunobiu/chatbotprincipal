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
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-100 rounded-full text-blue-700 text-[10px] font-medium mb-3"
                        >
                            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                            Automação com IA
                        </motion.div>

                        <motion.h1
                            variants={itemVariants}
                            className="text-2xl sm:text-3xl lg:text-4xl font-bold leading-tight mb-3"
                        >
                            Transforme cada{' '}
                            <span className="text-gradient">conversa</span> em uma{' '}
                            <span className="text-gradient">oportunidade</span>
                        </motion.h1>

                        <motion.p
                            variants={itemVariants}
                            className="text-sm sm:text-base text-gray-600 mb-4 max-w-lg mx-auto lg:mx-0"
                        >
                            Venda mais e aumente seu engajamento com automações inteligentes para WhatsApp e redes sociais.
                        </motion.p>

                        <motion.div
                            variants={itemVariants}
                            className="flex flex-col sm:flex-row gap-2.5 justify-center lg:justify-start"
                        >
                            <Link href="/login" scroll={true}>
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    className="btn-primary text-sm"
                                >
                                    <span>Teste Grátis por 7 Dias</span>
                                </motion.button>
                            </Link>
                            <a href="#como-funciona">
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    className="btn-secondary text-sm"
                                >
                                    Ver Demonstração
                                </motion.button>
                            </a>
                        </motion.div>

                        {/* Trust badges */}
                        <motion.div
                            variants={itemVariants}
                            className="mt-4 flex items-center gap-3 justify-center lg:justify-start text-xs"
                        >
                            <div className="flex items-center gap-1.5">
                                <div className="flex -space-x-1.5">
                                    {[1, 2, 3, 4].map((i) => (
                                        <div
                                            key={i}
                                            className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 border-2 border-white"
                                        />
                                    ))}
                                </div>
                                <span className="text-[10px] text-gray-600">
                                    +1M empresas
                                </span>
                            </div>
                            <div className="h-4 w-px bg-gray-300" />
                            <div className="flex items-center gap-0.5">
                                {[1, 2, 3, 4, 5].map((i) => (
                                    <svg key={i} className="w-3 h-3 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                    </svg>
                                ))}
                                <span className="text-[10px] text-gray-600 ml-0.5">4.9/5</span>
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
                        <div className="relative w-[240px] sm:w-[280px]">
                            {/* Phone frame */}
                            <div className="relative bg-gray-900 rounded-[2.5rem] p-2 shadow-2xl shadow-blue-500/20">
                                <div className="bg-white rounded-[2rem] overflow-hidden">
                                    {/* Phone header */}
                                    <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-2.5">
                                        <div className="flex items-center gap-2">
                                            <div className="w-7 h-7 bg-white/20 rounded-full flex items-center justify-center">
                                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                                                </svg>
                                            </div>
                                            <div>
                                                <p className="font-semibold text-xs">IA Bot</p>
                                                <p className="text-[9px] opacity-80">Online</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Chat area */}
                                    <div className="p-2.5 h-[320px] bg-gray-50 space-y-2.5 overflow-hidden">
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
                                                    className={`max-w-[80%] p-2 rounded-xl text-[11px] ${bubble.isBot
                                                            ? 'bg-white shadow-md rounded-bl-none'
                                                            : 'bg-blue-600 text-white rounded-br-none'
                                                        }`}
                                                >
                                                    {bubble.isBot && (
                                                        <div className="flex items-center gap-1 mb-0.5">
                                                            <div className="w-3 h-3 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full" />
                                                            <span className="text-[9px] font-medium text-blue-600">IA Bot</span>
                                                        </div>
                                                    )}
                                                    <p>{bubble.text}</p>
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
                                            <div className="bg-white shadow-md p-2 rounded-xl rounded-bl-none">
                                                <div className="flex gap-0.5">
                                                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
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
                                className="absolute -left-10 top-16 bg-white p-2 rounded-lg shadow-lg"
                            >
                                <div className="flex items-center gap-1.5">
                                    <span className="text-lg">📈</span>
                                    <div>
                                        <p className="text-[9px] text-gray-500">Conversões</p>
                                        <p className="text-xs font-bold text-green-600">+90%</p>
                                    </div>
                                </div>
                            </motion.div>

                            <motion.div
                                animate={{ y: [10, -10, 10] }}
                                transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
                                className="absolute -right-8 bottom-24 bg-white p-2 rounded-lg shadow-lg"
                            >
                                <div className="flex items-center gap-1.5">
                                    <span className="text-lg">⏱️</span>
                                    <div>
                                        <p className="text-[9px] text-gray-500">Resposta</p>
                                        <p className="text-xs font-bold text-blue-600">Instantâneo</p>
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
