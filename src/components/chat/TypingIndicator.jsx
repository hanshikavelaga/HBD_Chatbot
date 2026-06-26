import React from 'react';

export default function TypingIndicator({ status }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 16 }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
      }}>
        {/* Bot avatar */}
        <div style={{
          width: 28,
          height: 28,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 13,
          flexShrink: 0,
        }}>
          🐝
        </div>

        {/* Dots + Status text container */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <div style={{
            background: 'var(--chat-bot-bg)',
            border: '1px solid var(--chat-bot-border)',
            borderRadius: '4px 18px 18px 18px',
            padding: '10px 14px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
            boxShadow: 'var(--shadow-sm)',
          }}>
            <div className="typing-dot" />
            <div className="typing-dot" />
            <div className="typing-dot" />
          </div>
          {status && (
            <span style={{
              fontSize: '0.6875rem',
              color: 'var(--text-muted)',
              paddingLeft: 4,
              animation: 'pulse 1.5s infinite',
              fontWeight: 500
            }}>
              {status}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

