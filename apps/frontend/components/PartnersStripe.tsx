'use client';

import { motion } from 'framer-motion';

const partners = [
    { name: 'Nike', logo: '✓' },
    { name: 'Hotmart', logo: '🔥' },
    { name: 'Meta', logo: '◯' },
    { name: 'Mindvalley', logo: '✦' },
    { name: 'Shopify', logo: '🛒' },
    { name: 'Stripe', logo: '💳' },
    { name: 'Google', logo: 'G' },
];

export default function PartnersStripe() {
    return (
        <section className="py-12 border-y border-gray-100 bg-white">
            <div className="container-custom mb-8">
                <motion.h3
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center text-lg font-semibold text-gray-500"
                >
                    Aprovada por mais de 1 milhão de empresas e creators
                </motion.h3>
            </div>

            {/* Infinite scroll */}
            <div className="relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-40 bg-gradient-to-r from-white to-transparent z-10" />
                <div className="absolute right-0 top-0 bottom-0 w-40 bg-gradient-to-l from-white to-transparent z-10" />

                <div className="flex animate-scroll">
                    {[...partners, ...partners].map((partner, index) => (
                        <motion.div
                            key={`${partner.name}-${index}`}
                            whileHover={{ scale: 1.1 }}
                            className="flex items-center justify-center min-w-[200px] h-16 mx-8"
                        >
                            <div className="flex items-center gap-3 text-gray-400 hover:text-gray-600 transition-colors">
                                <span className="text-3xl">{partner.logo}</span>
                                <span className="text-xl font-bold tracking-tight">{partner.name}</span>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
