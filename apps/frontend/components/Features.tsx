'use client';

import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

const features = [
    {
        title: 'Colete mais leads',
        description: 'Ganhe mais seguidores e aumente sua monetização com engajamento de qualidade nas redes sociais. Use uma solução integrada para alcançar seu público onde quer que esteja.',
        video: '📊',
        stats: { label: 'Aumento de leads', value: '+150%' },
        reversed: false,
    },
    {
        title: 'Do like ao lucro: aumente as conversões em 90%',
        description: 'Gerencie sua base de leads de forma inteligente e utilize dados estratégicos para reengajar seus contatos nos momentos certos.',
        video: '💰',
        stats: { label: 'Taxa de conversão', value: '+90%' },
        reversed: true,
    },
    {
        title: 'Não deixe ninguém sem resposta',
        description: 'Automatize respostas e reações a cada curtida, comentário ou mensagem, e mantenha o engajamento 24h/dia.',
        video: '⚡',
        stats: { label: 'Tempo de resposta', value: '<1s' },
        reversed: false,
    },
    {
        title: 'Economize tempo na gestão das redes sociais',
        description: 'Automatize tarefas repetitivas e foque na criação de conteúdo de qualidade.',
        video: '⏰',
        stats: { label: 'Horas economizadas', value: '10h/sem' },
        reversed: true,
    },
    {
        title: 'Não precisa ter experiência em tecnologia!',
        description: 'As automações são intuitivas, no formato "arraste e solte", ideais para quem quer implementar fluxos de forma rápida.',
        video: '🧩',
        stats: { label: 'Setup rápido', value: '5 min' },
        reversed: false,
    },
];

function FeatureCard({ feature, index }: { feature: typeof features[0]; index: number }) {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-100px' });

    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0, y: 50 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className={`grid lg:grid-cols-2 gap-8 lg:gap-16 items-center ${feature.reversed ? 'lg:flex-row-reverse' : ''
                }`}
        >
            {/* Content */}
            <div className={`${feature.reversed ? 'lg:order-2' : 'lg:order-1'}`}>
                <motion.span
                    initial={{ opacity: 0, x: -20 }}
                    animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
                    transition={{ delay: 0.2 }}
                    className="inline-block px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4"
                >
                    Recurso {index + 1}
                </motion.span>

                <motion.h3
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                    transition={{ delay: 0.3 }}
                    className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4"
                >
                    {feature.title}
                </motion.h3>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                    transition={{ delay: 0.4 }}
                    className="text-lg text-gray-600 mb-6"
                >
                    {feature.description}
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
                    transition={{ delay: 0.5 }}
                    className="inline-flex items-center gap-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4"
                >
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center text-white text-2xl font-bold">
                        {feature.stats.value.charAt(0)}
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">{feature.stats.label}</p>
                        <p className="text-2xl font-bold text-gradient">{feature.stats.value}</p>
                    </div>
                </motion.div>
            </div>

            {/* Visual */}
            <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className={`${feature.reversed ? 'lg:order-1' : 'lg:order-2'}`}
            >
                <div className="relative aspect-square max-w-md mx-auto">
                    {/* Background decoration */}
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-100 to-purple-100 rounded-3xl transform rotate-3" />

                    {/* Main card */}
                    <div className="relative bg-white rounded-3xl shadow-xl p-8 flex items-center justify-center aspect-square">
                        <div className="text-8xl animate-float">{feature.video}</div>

                        {/* Floating stats */}
                        <motion.div
                            animate={{ y: [-10, 10, -10] }}
                            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                            className="absolute -top-4 -right-4 bg-white rounded-xl shadow-lg p-3"
                        >
                            <p className="text-xs text-gray-500">{feature.stats.label}</p>
                            <p className="text-lg font-bold text-green-600">{feature.stats.value}</p>
                        </motion.div>
                    </div>
                </div>
            </motion.div>
        </motion.div>
    );
}

export default function Features() {
    return (
        <section id="features" className="section-padding bg-gray-50">
            <div className="container-custom">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
                        Abra uma conversa.{' '}
                        <span className="text-gradient">Feche um negócio.</span>
                    </h2>
                    <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                        Automaticamente, 24 horas por dia, 7 dias por semana.
                    </p>
                </motion.div>

                <div className="space-y-24 lg:space-y-32">
                    {features.map((feature, index) => (
                        <FeatureCard key={feature.title} feature={feature} index={index} />
                    ))}
                </div>

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
                        <span>Comece gratuitamente</span>
                    </motion.button>
                </motion.div>
            </div>
        </section>
    );
}
