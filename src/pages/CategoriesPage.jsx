import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Grid, Search, ChevronRight, Tag, RefreshCw, ArrowRight,
  Dumbbell, Utensils, Sparkles, HeartPulse, GraduationCap, 
  ShoppingBag, Car, Briefcase
} from 'lucide-react';
import { api } from '../services/api';
import { CategoryCardSkeleton } from '../components/ui/Skeleton';

// Japanese-inspired delicate colors
const ACENT_COLORS = [
  '#5a52a3', // Soft Indigo
  '#4a6b5c', // Moss Green
  '#a36e52', // Soft Terracotta
  '#6b52a3', // Soft Iris
  '#3f5a6b', // Slate Blue
  '#a35265', // Sakura Gold/Red
];

const ICON_COMPONENTS = {
  Dumbbell: Dumbbell,
  Utensils: Utensils,
  Sparkles: Sparkles,
  HeartPulse: HeartPulse,
  GraduationCap: GraduationCap,
  ShoppingBag: ShoppingBag,
  Car: Car,
  Briefcase: Briefcase,
  Tag: Tag
};

export default function CategoriesPage({ toast, session }) {
  const navigate = useNavigate();
  const [parentCategories, setParentCategories] = useState([]);
  const [activeParentId, setActiveParentId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchCategories = () => {
    setLoading(true);
    api.getCategories(true)
      .then(data => {
        const parents = Array.isArray(data) ? data : [];
        setParentCategories(parents);
        if (parents.length > 0) {
          // Keep active parent selection if valid, else select first
          const exists = parents.some(p => p.id === activeParentId);
          if (!exists) {
            setActiveParentId(parents[0].id);
          }
        }
      })
      .catch(() => toast?.error('Failed to load categories'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const getFilteredSubcategories = () => {
    if (searchTerm.trim() !== '') {
      let results = [];
      parentCategories.forEach(parent => {
        if (parent.subcategories) {
          parent.subcategories.forEach(sub => {
            if (sub.name.toLowerCase().includes(searchTerm.toLowerCase())) {
              results.push({
                ...sub,
                parentName: parent.name,
                parentIcon: parent.icon
              });
            }
          });
        }
      });
      return results;
    } else {
      const activeParent = parentCategories.find(p => p.id === activeParentId);
      return activeParent?.subcategories || [];
    }
  };

  const handleCategoryClick = (name) => {
    let city = session?.city || localStorage.getItem('userCity');
    if (!city) {
      city = window.prompt("Please enter your city to find businesses near you:", "Surat");
      if (city) {
        localStorage.setItem('userCity', city);
      }
    }
    if (city) {
      navigate(`/chat?q=${encodeURIComponent(`${name} in ${city}`)}`);
    } else {
      navigate(`/chat?q=${encodeURIComponent(`find ${name} near me`)}`);
    }
  };

  const filteredSubs = getFilteredSubcategories();

  return (
    <div 
      style={{ 
        flex: 1, 
        overflowY: 'auto', 
        background: 'var(--bg-base)',
        padding: '24px 32px'
      }} 
      className="no-scrollbar"
    >
      {/* ─── HEADER ─────────────────────────── */}
      <div style={{
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: 24,
        marginBottom: 32,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-end',
        flexWrap: 'wrap',
        gap: 16,
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span style={{ 
              fontSize: '0.625rem', 
              fontWeight: 800, 
              letterSpacing: '0.15em', 
              color: 'var(--color-primary)', 
              textTransform: 'uppercase',
              background: 'var(--color-primary-light)',
              padding: '3px 8px',
              borderRadius: 4
            }}>
              Discover
            </span>
          </div>
          <h1 style={{ 
            fontSize: '1.625rem', 
            fontWeight: 800, 
            color: 'var(--text-primary)', 
            letterSpacing: '-0.02em',
            margin: 0
          }}>
            Business Categories
          </h1>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Explore local services, shops, and businesses curated by category
          </p>
        </div>

        {/* Refresh button */}
        <button
          onClick={fetchCategories}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '8px 14px',
            borderRadius: 8,
            border: '1px solid var(--border-subtle)',
            background: 'var(--bg-surface)',
            color: 'var(--text-secondary)',
            fontWeight: 600,
            fontSize: '0.75rem',
            cursor: 'pointer',
            transition: 'all 200ms ease'
          }}
          onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--color-primary)'}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
        >
          <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
          Reload
        </button>
      </div>

      {/* ─── SEARCH & FILTER BAR ─────────────────────────────── */}
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 12,
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        maxWidth: 480,
        marginBottom: 32,
        boxShadow: 'var(--shadow-sm)'
      }}>
        <Search size={16} style={{ color: 'var(--text-muted)' }} />
        <input 
          type="text"
          placeholder="Search categories..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          style={{
            flex: 1,
            border: 'none',
            outline: 'none',
            fontSize: '0.875rem',
            background: 'transparent',
            color: 'var(--text-primary)',
          }}
        />
        {searchTerm && (
          <button 
            onClick={() => setSearchTerm('')}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              cursor: 'pointer'
            }}
          >
            Clear
          </button>
        )}
      </div>

      {/* ─── PARENT CATEGORY TABS (Hidden when searching) ────────────────── */}
      {!searchTerm && !loading && parentCategories.length > 0 && (
        <div style={{
          display: 'flex',
          gap: 10,
          overflowX: 'auto',
          paddingBottom: 16,
          marginBottom: 24,
          borderBottom: '1px solid var(--border-subtle)'
        }} className="no-scrollbar">
          {parentCategories.map((parent) => {
            const ParentIcon = ICON_COMPONENTS[parent.icon] || Tag;
            const isSelected = activeParentId === parent.id;
            return (
              <button
                key={parent.id}
                onClick={() => setActiveParentId(parent.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 16px',
                  borderRadius: 20,
                  border: isSelected ? '1px solid var(--color-primary)' : '1px solid var(--border-subtle)',
                  background: isSelected ? 'var(--color-primary-light)' : 'var(--bg-surface)',
                  color: isSelected ? 'var(--color-primary)' : 'var(--text-secondary)',
                  fontWeight: 700,
                  fontSize: '0.8125rem',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 200ms ease'
                }}
              >
                <ParentIcon size={14} />
                <span>{parent.name}</span>
                <span style={{
                  fontSize: '0.6875rem',
                  opacity: 0.8,
                  background: isSelected ? 'var(--color-primary)' : 'var(--bg-surface-2)',
                  color: isSelected ? '#fff' : 'var(--text-muted)',
                  padding: '1px 6px',
                  borderRadius: 10,
                  marginLeft: 4
                }}>
                  {parent.count}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* ─── MAIN GRID ─────────────────────────────────────────── */}
      {loading ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
          gap: 16
        }}>
          {[...Array(12)].map((_, i) => <CategoryCardSkeleton key={i} />)}
        </div>
      ) : filteredSubs.length > 0 ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
          gap: 16
        }}>
          {filteredSubs.map((sub, i) => {
            const name = sub.name || 'Unknown';
            const count = sub.count ?? 0;
            const accentColor = ACENT_COLORS[i % ACENT_COLORS.length];
            const SubIcon = ICON_COMPONENTS[sub.icon] || Tag;

            return (
              <div
                key={sub.id || i}
                onClick={() => handleCategoryClick(name)}
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 12,
                  padding: '20px 22px',
                  cursor: 'pointer',
                  transition: 'all 250ms cubic-bezier(0.16, 1, 0.3, 1)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  height: 120,
                  position: 'relative',
                  overflow: 'hidden'
                }}
                className="category-page-card"
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.borderColor = accentColor;
                  e.currentTarget.style.boxShadow = `0 6px 20px ${accentColor}12`;
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'none';
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                {/* Thin side color indicator */}
                <div style={{
                  position: 'absolute',
                  left: 0,
                  top: 0,
                  bottom: 0,
                  width: 3,
                  background: accentColor
                }} />

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{
                    width: 32,
                    height: 32,
                    borderRadius: 8,
                    background: `${accentColor}12`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: accentColor
                  }}>
                    <SubIcon size={14} />
                  </div>
                  
                  <span style={{
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    color: 'var(--text-muted)',
                    background: 'var(--bg-surface-2)',
                    padding: '2px 8px',
                    borderRadius: 10
                  }}>
                    {count} {count === 1 ? 'listing' : 'listings'}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 12 }}>
                  <div>
                    <h3 style={{
                      fontSize: '0.875rem',
                      fontWeight: 700,
                      color: 'var(--text-primary)',
                      margin: 0,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      maxWidth: 180
                    }}>
                      {name}
                    </h3>
                    {searchTerm && (
                      <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                        in {sub.parentName}
                      </span>
                    )}
                  </div>
                  <ChevronRight size={14} style={{ color: 'var(--text-muted)' }} />
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '64px 0',
          border: '1px dashed var(--border-subtle)',
          borderRadius: 12,
          background: 'var(--bg-surface)',
          maxWidth: 480,
          margin: '0 auto'
        }}>
          <Grid size={32} style={{ color: 'var(--text-muted)', opacity: 0.5, marginBottom: 12 }} />
          <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            No categories found matching "{searchTerm}"
          </p>
          <button 
            onClick={() => setSearchTerm('')}
            style={{
              marginTop: 12,
              padding: '6px 14px',
              borderRadius: 6,
              background: 'var(--color-primary-light)',
              color: 'var(--color-primary)',
              border: 'none',
              fontSize: '0.75rem',
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            Reset Search
          </button>
        </div>
      )}
    </div>
  );
}
