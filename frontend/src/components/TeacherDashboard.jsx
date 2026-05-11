"""
TeacherDashboard.jsx - O'qituvchi Paneli
Real-time analytics va smart recommendations
"""

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function TeacherDashboard() {
  const [students, setStudents] = useState([]);
  const [filter, setFilter] = useState('all'); // 'all', 'needs_help', 'excellent'
  const [loading, setLoading] = useState(true);

  // Dashboard'ni yuklash
  const loadDashboard = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/teacher/dashboard`, {
        params: { filter_status: filter === 'all' ? null : filter }
      });
      
      setStudents(response.data.students_analytics);
      setLoading(false);
    } catch (error) {
      console.error('Dashboard load xatosi:', error);
      setLoading(false);
    }
  };

  // Dastlabki yuklash va har 5 soniyada yangilash
  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 5000);
    return () => clearInterval(interval);
  }, [filter]);

  const getStatusColor = (status) => {
    if (status === 'needs_help') return 'bg-red-100 border-red-300';
    if (status === 'excellent') return 'bg-green-100 border-green-300';
    return 'bg-yellow-100 border-yellow-300';
  };

  const getProgressColor = (score) => {
    if (score >= 4) return 'bg-green-500';
    if (score >= 3) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusEmoji = (status) => {
    if (status === 'needs_help') return '⚠️';
    if (status === 'excellent') return '✅';
    return '⏳';
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">
          👩‍🏫 O'qituvchi Paneli
        </h2>
        
        {/* Filter Buttons */}
        <div className="flex gap-3 mb-6">
          <button
            onClick={() => setFilter('all')}
            className={`px-6 py-2 rounded-lg font-medium transition ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Barchasi ({students.length})
          </button>
          <button
            onClick={() => setFilter('needs_help')}
            className={`px-6 py-2 rounded-lg font-medium transition ${
              filter === 'needs_help'
                ? 'bg-red-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Yordam Kerak ⚠️
          </button>
          <button
            onClick={() => setFilter('excellent')}
            className={`px-6 py-2 rounded-lg font-medium transition ${
              filter === 'excellent'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            A'lo ✅
          </button>
        </div>
      </div>

      {/* Student Cards Grid */}
      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">⏳ Yuklanyapti...</p>
        </div>
      ) : students.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">
            Hozircha o'quvchi mavjud emas. 
            O'quvchi sida dars boshlashni kutamiz.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {students.map((student) => (
            <div
              key={student.student_name}
              className={`rounded-lg shadow-lg p-6 border-2 transition hover:shadow-xl ${getStatusColor(student.status)}`}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-800">
                  {student.student_name}
                </h3>
                <span className="text-2xl">{getStatusEmoji(student.status)}</span>
              </div>

              {/* Progress Bars */}
              <div className="space-y-3 mb-6">
                {/* Mantiqiy Fikrlash */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-sm font-medium text-gray-700">
                      🧠 Mantiq
                    </label>
                    <span className="text-sm font-bold text-gray-800">
                      {student.logical_thinking}/5
                    </span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getProgressColor(student.logical_thinking)}`}
                      style={{ width: `${(student.logical_thinking / 5) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Mavzuni Tushunish */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-sm font-medium text-gray-700">
                      📖 Tushuncha
                    </label>
                    <span className="text-sm font-bold text-gray-800">
                      {student.concept_understanding}/5
                    </span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getProgressColor(student.concept_understanding)}`}
                      style={{ width: `${(student.concept_understanding / 5) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Motivatsiya */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-sm font-medium text-gray-700">
                      ⚡ Motivatsiya
                    </label>
                    <span className="text-sm font-bold text-gray-800">
                      {student.motivation}/5
                    </span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getProgressColor(student.motivation)}`}
                      style={{ width: `${(student.motivation / 5) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Recommendation */}
              <div className="bg-white bg-opacity-60 rounded p-3 mb-4">
                <p className="text-xs font-medium text-gray-600 mb-1">💡 Tavsiya:</p>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {student.recommendation}
                </p>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-2 text-center text-xs">
                <div className="bg-blue-200 rounded py-1">
                  <p className="font-bold text-blue-800">
                    {student.message_count}
                  </p>
                  <p className="text-blue-700">Xabar</p>
                </div>
                <div className="bg-purple-200 rounded py-1">
                  <p className="font-bold text-purple-800">
                    {student.sessions_count}
                  </p>
                  <p className="text-purple-700">Sessiya</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Last Update Info */}
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>🔄 Har 5 soniyada avtomatik yangilash | Last updated: {new Date().toLocaleTimeString()}</p>
      </div>
    </div>
  );
}

export default TeacherDashboard;
