import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import Sidebar from './sidebar/Sidebar';
import { useTheme } from '../hooks/useTheme';
import ChatArea from './chat/ChatArea';

export default function Layout(props) {
  const {
    isLoggedIn, setIsLoggedIn,
    session, setSession,
    currentSessionId, setCurrentSessionId,
    chatList, setChatList,
    chatListLoading, setChatListLoading,
    onNewChat,
    onLoadSession,
    onDeleteSession,
    onRenameSession,
    onPinSession,
    toast,
  } = props;
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [showFloatingChat, setShowFloatingChat] = useState(false);

  // Close mobile sidebar when window resizes to desktop
  useEffect(() => {
    const handler = () => {
      if (window.innerWidth > 768) setMobileOpen(false);
    };
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);

  const handleLogout = () => {
    setIsLoggedIn(false);
    setSession({ type: 'GUEST', phone: null, email: null, businessId: null });
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('session');
    if (setCurrentSessionId) setCurrentSessionId(null);
    if (setChatList) setChatList([]);
    toast?.success('Logged out successfully');
    navigate('/');
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
        isLoggedIn={isLoggedIn}
        session={session}
        onLogout={handleLogout}
        chatList={chatList || []}
        chatListLoading={chatListLoading || false}
        currentSessionId={currentSessionId}
        onNewChat={onNewChat}
        onLoadSession={onLoadSession}
        onDeleteSession={onDeleteSession}
        onRenameSession={onRenameSession}
        onPinSession={onPinSession}
        onLoadChatList={() => {}}
        isDark={isDark}
        onToggleTheme={toggleTheme}
      />

      {/* Main content */}
      <div className="main-content">
        {/* Mobile top bar */}
        <div style={{
          display: 'none',
          padding: '12px 16px',
          background: 'var(--bg-surface)',
          borderBottom: '1px solid var(--border-subtle)',
          alignItems: 'center',
          gap: 12,
          position: 'sticky', top: 0, zIndex: 30,
        }}
          id="mobile-topbar"
          className="mobile-topbar"
        >
          <button
            onClick={() => setMobileOpen(true)}
            style={{
              padding: 7, borderRadius: 8, border: 'none',
              background: 'var(--bg-surface-2)', cursor: 'pointer',
              color: 'var(--text-secondary)', display: 'flex', alignItems: 'center',
            }}
            aria-label="Open sidebar"
          >
            <Menu size={18} />
          </button>
          <div style={{
            width: 28, height: 28, background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
            borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14,
          }}>🐝</div>
          <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--text-primary)' }}>CityHangAround AI</span>
        </div>

        {/* Page content */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Outlet />
        </div>
      </div>

      {/* Floating Chatbot Widget (Myntra-style) */}
      {location.pathname !== '/chat' && (
        <>
          {showFloatingChat && (
            <div className="floating-chat-widget">
              <ChatArea
                {...props}
                isFloating={true}
                onClose={() => setShowFloatingChat(false)}
              />
            </div>
          )}
          
          <button
            className="floating-chat-launcher"
            onClick={() => setShowFloatingChat(!showFloatingChat)}
            aria-label={showFloatingChat ? "Close chat assistant" : "Open chat assistant"}
          >
            {showFloatingChat ? (
              <X size={24} style={{ color: 'white' }} />
            ) : (
              <img src="/avatar.png" alt="AI Assistant Avatar" />
            )}
          </button>
        </>
      )}
    </div>
  );
}