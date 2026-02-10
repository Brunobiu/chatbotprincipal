'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';

const navItems = [
    { label: 'Canais', href: '#canais' },
    { label: 'Recursos', href: '#recursos' },
    { label: 'Depoimentos', href: '#depoimentos' },
    { label: 'Como Funciona', href: '#como-funciona' },
];

export default function Header() {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <header
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
                    ? 'py-3 bg-white/90 backdrop-blur-lg shadow-soft'
                    : 'py-5 bg-transparent'
                }`}
        >
            <div className="container-custom">
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <motion.div
                            whileHover={{ scale: 1.05 }}
                            className="flex items-center gap-2"
                        >
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-cyan-500 rounded-xl flex items-center justify-center">
                                <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                                </svg>
                            </div>
                            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
                                IA Bot
                            </span>
                        </motion.div>
                    </Link>

                    {/* Desktop Navigation */}
                    <nav className="hidden lg:flex items-center gap-8">
                        {navItems.map((item) => (
                            <Link
                                key={item.label}
                                href={item.href}
                                className="relative text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors group"
                            >
                                {item.label}
                                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full" />
                            </Link>
                        ))}
                    </nav>

                    {/* CTA Buttons */}
                    <div className="hidden lg:flex items-center gap-4">
                        <Link
                            href="/login"
                            className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
                        >
                            Entrar
                        </Link>
                        <Link href="/login">
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className="btn-primary text-sm"
                            >
                                <span>Começar Grátis</span>
                            </motion.button>
                        </Link>
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="lg:hidden relative w-10 h-10 flex flex-col items-center justify-center gap-1.5"
                    >
                        <motion.span
                            animate={isMobileMenuOpen ? { rotate: 45, y: 6 } : { rotate: 0, y: 0 }}
                            className="w-6 h-0.5 bg-gray-800 rounded-full"
                        />
                        <motion.span
                            animate={isMobileMenuOpen ? { opacity: 0 } : { opacity: 1 }}
                            className="w-6 h-0.5 bg-gray-800 rounded-full"
                        />
                        <motion.span
                            animate={isMobileMenuOpen ? { rotate: -45, y: -6 } : { rotate: 0, y: 0 }}
                            className="w-6 h-0.5 bg-gray-800 rounded-full"
                        />
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="lg:hidden bg-white border-t shadow-lg overflow-hidden"
                    >
                        <div className="container-custom py-6 flex flex-col gap-4">
                            {navItems.map((item, index) => (
                                <motion.div
                                    key={item.label}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                >
                                    <Link
                                        href={item.href}
                                        onClick={() => setIsMobileMenuOpen(false)}
                                        className="block py-2 text-lg font-medium text-gray-700 hover:text-blue-600"
                                    >
                                        {item.label}
                                    </Link>
                                </motion.div>
                            ))}
                            <hr className="my-2" />
                            <Link href="/login" className="py-2 text-gray-700">
                                Entrar
                            </Link>
                            <Link href="/login">
                                <motion.button
                                    whileTap={{ scale: 0.98 }}
                                    className="btn-primary w-full text-center"
                                >
                                    <span>Começar Grátis</span>
                                </motion.button>
                            </Link>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </header>
    );
}
