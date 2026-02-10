'use client';

import { motion, useInView } from 'framer-motion';
import { useRef, useEffect, useState } from 'react';

const stats = [
    { value: 1000000, suffix: '+', label: 'de marcas e creators', subtext: 'escolheram nossa plataforma' },
    { value: 1000000000, suffix: '+', label: 'de conversas', subtext: 'geradas no Brasil em 2024' },
    { value: 170, suffix: '+', label: 'países', subtext: 'utilizam a plataforma' },
    { value: 60, suffix: '%', label: 'dos usuários', subtext: 'usam integração de canais' },
];

function formatNumber(num: number): string {
    if (num >= 1000000000) return (num / 1000000000).toFixed(0) + 'B';
    if (num >= 1000000) return (num / 1000000).toFixed(0) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(0) + 'K';
    return num.toString();
}

function AnimatedNumber({ value, suffix, inView }: { value: number; suffix: string; inView: boolean }) {
    const [displayValue, setDisplayValue] = useState(0);

    useEffect(() => {
        if (inView) {
            const duration = 2000;
            const steps = 60;
            const increment = value / steps;
            let current = 0;

            const timer = setInterval(() => {
                current += increment;
                if (current >= value) {
                    setDisplayValue(value);
                    clearInterval(timer);
                } else {
                    setDisplayValue(Math.floor(current));
                }
            }, duration / steps);

            return () => clearInterval(timer);
        }
    }, [inView, value]);

    return (
        <span className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gradient">
            {formatNumber(displayValue)}{suffix}
        </span>
    );
}

export default function Stats() {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-100px' });

    return (
        <section className="section-padding bg-white" ref={ref}>
            <div className="container-custom">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-8"
                >
                    <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold mb-1.5">
                        Saiba por que somos a{' '}
                        <span className="text-gradient">#1 em automação</span>
                    </h2>
                </motion.div>

                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {stats.map((stat, index) => (
                        <motion.div
                            key={stat.label}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            className="text-center"
                        >
                            <AnimatedNumber value={stat.value} suffix={stat.suffix} inView={isInView} />
                            <p className="text-sm font-semibold text-gray-800 mt-1">{stat.label}</p>
                            <p className="text-gray-500 text-[10px]">{stat.subtext}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
