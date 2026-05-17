import React from 'react';
import { Document, Page, Text, View, StyleSheet, Font } from '@react-pdf/renderer';

// Create styles for the PDF
const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    padding: 30,
    fontFamily: 'Helvetica',
  },
  header: {
    marginBottom: 10,
  },
  name: {
    fontSize: 24,
    fontFamily: 'Helvetica-Bold',
    textAlign: 'center',
    marginBottom: 5,
  },
  contact: {
    fontSize: 10,
    textAlign: 'center',
    color: '#333333',
  },
  section: {
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 14,
    fontFamily: 'Helvetica-Bold',
    marginBottom: 3,
    borderBottomWidth: 1,
    borderBottomColor: '#CCCCCC',
    borderBottomStyle: 'solid',
    paddingBottom: 1,
    textTransform: 'uppercase',
  },
  content: {
    fontSize: 10,
    lineHeight: 1.5,
  },
  bulletPoint: {
    flexDirection: 'row',
    marginBottom: 2,
  },
  bullet: {
    width: 15,
    fontSize: 10,
  },
  bulletText: {
    flex: 1,
    fontSize: 10,
    lineHeight: 1.5,
  }
});

// Helper to parse simple markdown lists
const renderMarkdownText = (text) => {
  if (!text) return null;

  const lines = text.split('\n');
  return lines.map((line, index) => {
    const trimmed = line.trim();
    if (!trimmed) return null;

    // Check if it's a list item
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      return (
        <View key={index} style={styles.bulletPoint}>
          <Text style={styles.bullet}>•</Text>
          <Text style={styles.bulletText}>{trimmed.substring(2)}</Text>
        </View>
      );
    }

    // Check if it's a bold header (like **Job Title**)
    // We do a simple fallback by just removing ** for now, 
    // or rendering it in a View if we want bold.
    let content = trimmed;
    content = content.replace(/\*\*(.*?)\*\*/g, '$1'); // Strip bold for simplicity in basic text
    content = content.replace(/__(.*?)__/g, '$1');
    content = content.replace(/\*(.*?)\*/g, '$1');

    // Ignore markdown headers inside sections to keep it clean
    if (trimmed.startsWith('### ')) {
      return <Text key={index} style={{ ...styles.content, fontFamily: 'Helvetica-Bold', marginTop: 5 }}>{trimmed.substring(4)}</Text>;
    }
    if (trimmed.startsWith('## ')) {
      return <Text key={index} style={{ ...styles.content, fontFamily: 'Helvetica-Bold', marginTop: 8 }}>{trimmed.substring(3)}</Text>;
    }
    if (trimmed.startsWith('# ')) return null; // handled in titles

    return <Text key={index} style={styles.content}>{content}</Text>;
  });
};

const ensureString = (val) => {
  if (Array.isArray(val)) return val.join(', ');
  if (typeof val === 'object' && val !== null) {
    return Object.values(val).filter(Boolean).join(' | ');
  }
  return String(val || '');
};

const ResumePDFTemplate = ({ resumeData }) => {
  if (!resumeData) return null;

  // Handle case where we still got a string (legacy)
  const isString = typeof resumeData === 'string';
  if (isString) {
    return (
      <Document>
        <Page size="A4" style={styles.page}>
          <View style={styles.section}>
            {renderMarkdownText(resumeData)}
          </View>
        </Page>
      </Document>
    );
  }

  const { name, contact, summary, experience, education, skills, projects } = resumeData;

  return (
    <Document>
      <Page size="A4" style={styles.page}>

        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.name}>{ensureString(name)}</Text>
          <Text style={styles.contact}>{ensureString(contact).replace(/\n/g, ' | ')}</Text>
        </View>

        {/* Summary */}
        {summary && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Professional Summary</Text>
            <Text style={styles.content}>{ensureString(summary)}</Text>
          </View>
        )}

        {/* Experience */}
        {experience && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Experience</Text>
            {Array.isArray(experience) ? experience.map((item, idx) => {
              if (typeof item === 'string') return renderMarkdownText(item);
              return (
                <View key={idx} style={{ marginBottom: idx === experience.length - 1 ? 0 : 6 }}>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 2 }}>
                    <Text style={{ ...styles.content, fontFamily: 'Helvetica-Bold' }}>
                      {item.role || item.title} {item.company ? `, ${item.company}` : ''}
                    </Text>
                    <Text style={{ ...styles.content, color: '#666666' }}>
                      {[item.location, item.duration].filter(Boolean).join(' | ')}
                    </Text>
                  </View>
                  {item.responsibilities && Array.isArray(item.responsibilities) ? (
                    <>
                      {item.responsibilities.map((resp, rIdx) => (
                        <View key={rIdx} style={styles.bulletPoint}>
                          <Text style={styles.bullet}>•</Text>
                          <Text style={styles.bulletText}>{resp}</Text>
                        </View>
                      ))}
                      {item.skills && (
                        <View style={styles.bulletPoint}>
                          <Text style={styles.bullet}>•</Text>
                          <Text style={styles.bulletText}>
                            <Text style={{ fontFamily: 'Helvetica-Bold' }}>Skills: </Text>
                            {Array.isArray(item.skills) ? item.skills.join(', ') : item.skills}
                          </Text>
                        </View>
                      )}
                    </>
                  ) : item.responsibilities ? (
                    <>
                      {renderMarkdownText(String(item.responsibilities))}
                      {item.skills && (
                        <View style={styles.bulletPoint}>
                          <Text style={styles.bullet}>•</Text>
                          <Text style={styles.bulletText}>
                            <Text style={{ fontFamily: 'Helvetica-Bold' }}>Skills: </Text>
                            {Array.isArray(item.skills) ? item.skills.join(', ') : item.skills}
                          </Text>
                        </View>
                      )}
                    </>
                  ) : null}
                </View>
              );
            }) : renderMarkdownText(ensureString(experience))}
          </View>
        )}

        {/* Education */}
        {education && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Education</Text>
            {Array.isArray(education) ? education.map((item, idx) => {
              if (typeof item === 'string') return renderMarkdownText(item);
              return (
                <View key={idx} style={{ marginBottom: idx === education.length - 1 ? 0 : 5 }}>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 2 }}>
                    <Text style={{ ...styles.content, fontFamily: 'Helvetica-Bold' }}>
                      {item.degree || item.title}
                    </Text>
                    <Text style={{ ...styles.content, color: '#666666' }}>
                      {[item.location, item.duration].filter(Boolean).join(' | ')}
                    </Text>
                  </View>
                  {item.institution && (
                    <Text style={{ ...styles.content, color: '#333333' }}>
                      {item.institution}
                    </Text>
                  )}
                </View>
              );
            }) : renderMarkdownText(ensureString(education))}
          </View>
        )}
        {/* Projects */}
        {projects && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Projects</Text>
            {Array.isArray(projects) ? projects.map((item, idx) => {
              if (typeof item === 'string') return renderMarkdownText(item);
              return (
                <View key={idx} style={{ marginBottom: idx === projects.length - 1 ? 0 : 5 }}>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 2 }}>
                    <Text style={{ ...styles.content, fontFamily: 'Helvetica-Bold' }}>
                      {item.name}
                    </Text>
                    <Text style={{ ...styles.content, color: '#666666' }}>
                      {[item.duration].filter(Boolean).join(' | ')}
                    </Text>
                  </View>
                  {item.description && Array.isArray(item.description) ? (
                    item.description.map((desc, dIdx) => (
                      <View key={dIdx} style={styles.bulletPoint}>
                        <Text style={styles.bullet}>•</Text>
                        <Text style={styles.bulletText}>{desc}</Text>
                      </View>
                    ))
                  ) : item.description ? (
                    <Text style={{ ...styles.content, color: '#333333' }}>
                      {item.description}
                    </Text>
                  ) : null}
                </View>
              );
            }) : renderMarkdownText(ensureString(projects))}
          </View>
        )}
        {/* Skills */}
        {skills && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Skills</Text>
            <Text style={styles.content}>{ensureString(skills)}</Text>
          </View>
        )}
      </Page>
    </Document>
  );
};

export default ResumePDFTemplate;
