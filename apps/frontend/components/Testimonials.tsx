'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import Image from 'next/image';

const testimonials = [
    {
        name: 'Romina Thaler',
        role: 'Produtora Sênior, UNIT9',
        company: 'Nike Football',
        image: '👩‍💼',
        text: 'Com certeza voltaríamos a usar. A equipe foi muito prestativa ao responder às nossas dúvidas. A plataforma poderia ser usada para qualquer experiência de chatbot, incluindo campanhas com as interações mais criativas.',
        rating: 5,
    },
    {
        name: 'Jenna Kutcher',
        role: 'Especialista em Marketing Digital',
        company: '1M+ seguidores',
        image: '👩',
        text: 'Mudou toda a presença online da minha empresa. Eu consegui resultados reais com as redes sociais, atendendo os meus seguidores de um jeito totalmente único. É uma ferramenta essencial!',
        rating: 5,
    },
    {
        name: 'Theresa Dihn',
        role: 'Embaixadora do Notion',
        company: '22 mil seguidores',
        image: '👩‍🎓',
        text: 'É a melhor coisa que aconteceu comigo. Ela praticamente roda sozinha. Eu recebo tantos e-mails e downloads no Instagram. Com a automatização de comentários, consigo vender e tenho muito engajamento!',
        rating: 5,
    },
    {
        name: 'Kahlea Wade',
        role: 'Empreendedora',
        company: '24.4 mil seguidores',
        image: '👩‍💻',
        text: 'Nos ajudou a vender mais de US$70 mil em cursos em três semanas. Percebi um aumento INCRÍVEL nas conversões depois de apenas uma semana. É um investimento que triplicou o meu ROI!',
        rating: 5,
    },
];

export default function Testimonials() {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [direction, setDirection] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setDirection(1);
            setCurrentIndex((prev) => (prev + 1) % testimonials.length);
        }, 5000);
        return () => clearInterval(timer);
    }, []);

    const slideVariants = {
        enter: (direction: number) => ({
            x: direction > 0 ? 1000 : -1000,
            opacity: 0,
        }),
        center: {
            zIndex: 1,
            x: 0,
            opacity: 1,
        },
        exit: (direction: number) => ({
            zIndex: 0,
            x: direction < 0 ? 1000 : -1000,
            opacity: 0,
        }),
    };

    const goToSlide = (index: number) => {
        setDirection(index > currentIndex ? 1 : -1);
        setCurrentIndex(index);
    };

    const nextSlide = () => {
        setDirection(1);
        setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    };

    const prevSlide = () => {
        setDirection(-1);
        setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
    };

    return (
        <section className="section-padding bg-gray-50 overflow-hidden">
            <div className="container-custom">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-12"
                >
                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
                        O que nossos clientes dizem
                    </h2>
                    <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                        Milhares de empresas e criadores já transformaram seus negócios
                    </p>
                </motion.div>

                <div className="relative max-w-4xl mx-auto">
                    <AnimatePresence initial={false} custom={direction}>
                        <motion.div
                            key={currentIndex}
                            custom={direction}
                            variants={slideVariants}
                            initial="enter"
                            animate="center"
                            exit="exit"
                            transition={{ duration: 0.5, ease: 'easeInOut' }}
                            className="bg-white rounded-3xl shadow-xl p-8 sm:p-12"
                        >
                            <div className="grid md:grid-cols-5 gap-8 items-center">
                                {/* Image side */}
                                <div className="md:col-span-2">
                                    <div className="relative aspect-square max-w-xs mx-auto bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl flex items-center justify-center">
                                        <span className="text-8xl">{testimonials[currentIndex].image}</span>
                                    </div>
                                </div>

                                {/* Content side */}
                                <div className="md:col-span-3">
                                    {/* Quote */}
                                    <div className="text-5xl text-blue-200 mb-4">"</div>
                                    <p className="text-lg sm:text-xl text-gray-700 mb-6 italic">
                                        {testimonials[currentIndex].text}
                                    </p>

                                    {/* Rating */}
                                    <div className="flex gap-1 mb-4">
                                        {Array.from({ length: testimonials[currentIndex].rating }).map((_, i) => (
                                            <svg key={i} className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                            </svg>
                                        ))}
                                    </div>

                                    {/* Author */}
                                    <div>
                                        <p className="font-bold text-lg">{testimonials[currentIndex].name}</p>
                                        <p className="text-gray-500">{testimonials[currentIndex].role}</p>
                                        <p className="text-blue-600 font-medium">{testimonials[currentIndex].company}</p>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </AnimatePresence>

                    {/* Navigation Arrows */}
                    <button
                        onClick={prevSlide}
                        className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 sm:-translate-x-12 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                    </button>
                    <button
                        onClick={nextSlide}
                        className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 sm:translate-x-12 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                    </button>

                    {/* Dots */}
                    <div className="flex justify-center gap-2 mt-8">
                        {testimonials.map((_, index) => (
                            <button
                                key={index}
                                onClick={() => goToSlide(index)}
                                className={`w-3 h-3 rounded-full transition-all duration-300 ${index === currentIndex ? 'bg-blue-600 w-8' : 'bg-gray-300 hover:bg-gray-400'
                                    }`}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
