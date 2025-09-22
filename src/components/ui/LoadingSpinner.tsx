import React from 'react';
import { motion } from 'framer-motion';
import { Gamepad2, Zap } from 'lucide-react';

export const LoadingSpinner: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-900 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-40 left-40 w-60 h-60 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
      </div>

      <div className="text-center relative z-10">
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 0.8, type: "spring", stiffness: 100 }}
          className="relative"
        >
          <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-2xl mb-6 mx-auto">
            <Gamepad2 className="w-10 h-10 text-white" />
          </div>
          
          {/* Spinning Ring */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute -inset-4 border-4 border-transparent border-t-purple-500 border-r-blue-500 rounded-full"
          ></motion.div>
          
          {/* Inner Spinning Ring */}
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            className="absolute -inset-2 border-2 border-transparent border-b-pink-500 border-l-yellow-500 rounded-full"
          ></motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="space-y-2"
        >
          <h2 className="text-2xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
            Aries Esports
          </h2>
          <div className="flex items-center justify-center space-x-2">
            <Zap className="w-5 h-5 text-purple-400 animate-pulse" />
            <p className="text-purple-200">Loading your gaming universe...</p>
            <Zap className="w-5 h-5 text-purple-400 animate-pulse" />
          </div>
        </motion.div>
      </div>
    </div>
  );
};
