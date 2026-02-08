'use client';

import { motion } from 'framer-motion';

const steps = [
    {
        number: '1',
        title: 'Crie sua conta',
        description: 'Aproveite os 14 dias grátis de teste — sem compromisso.',
        icon: '🚀',
        color: 'from-blue-400 to-blue-600',
    },
    {
        number: '2',
        title: 'Configure suas automações',
        description: 'Use nossos templates prontos ou crie fluxos personalizados.',
        icon: '⚙️',
        color: 'from-purple-400 to-purple-600',
    },
    {
        number: '3',
        title: 'Acompanhe os resultados',
        description: 'Ajuste sua estratégia para crescer cada vez mais.',
        icon: '📈',
        color: 'from-green-400 to-green-600',
    },
];

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.2,
        },
    },
};

const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.5 },
    },
};

export default function Steps() {
    return (
        <section className="section-padding bg-white">
            <div className="container-custom">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
                        Como começar
                    </h2>
                    <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                        Em apenas 3 passos simples, você estará automatizando suas conversas
                    </p>
                </motion.div>

                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    className="grid md:grid-cols-3 gap-8"
                >
                    {steps.map((step, index) => (
                        <motion.div
                            key={step.number}
                            variants={itemVariants}
                            className="relative"
                        >
                            {/* Connector line */}
                            {index < steps.length - 1 && (
                                <div className="hidden md:block absolute top-20 left-1/2 w-full h-0.5 bg-gradient-to-r from-blue-200 to-purple-200" />
                            )}

                            <motion.div
                                whileHover={{ y: -5 }}
                                className="relative bg-gray-50 rounded-3xl p-8 h-full"
                            >
                                {/* Step number */}
                                <motion.div
                                    whileHover={{ scale: 1.1, rotate: 5 }}
                                    className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center text-white text-2xl font-bold mb-6 shadow-lg`}
                                >
                                    {step.number}
                                </motion.div>

                                {/* Icon */}
                                <div className="text-5xl mb-4">{step.icon}</div>

                                {/* Content */}
                                <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                                <p className="text-gray-600">{step.description}</p>

                                {/* Decorative element */}
                                <div className="absolute top-4 right-4 text-6xl opacity-10">
                                    {step.number}
                                </div>
                            </motion.div>
                        </motion.div>
                    ))}
                </motion.div>

                {/* CTA */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mt-16"
                >
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="btn-primary text-lg"
                    >
                        <span>Começar Gratuitamente</span>
                    </motion.button>
                </motion.div>
            </div>
        </section>
    );
}
