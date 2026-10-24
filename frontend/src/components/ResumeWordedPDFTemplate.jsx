import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: {
    paddingTop: 34,
    paddingBottom: 34,
    paddingHorizontal: 42,
    backgroundColor: '#FFFFFF',
    color: '#202124',
    fontFamily: 'Helvetica',
    fontSize: 9,
  },
  header: {
    marginBottom: 16,
  },
  name: {
    fontSize: 21,
    fontFamily: 'Helvetica-Bold',
    marginBottom: 5,
  },
  contact: {
    fontSize: 8,
    color: '#4B5563',
    lineHeight: 1.4,
  },
  section: {
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 10,
    fontFamily: 'Helvetica-Bold',
    color: '#1F2937',
    borderBottomWidth: 0.7,
    borderBottomColor: '#6B7280',
    paddingBottom: 3,
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  entry: {
    marginBottom: 7,
  },
  entryHeading: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 2,
  },
  entryTitle: {
    fontSize: 9,
    fontFamily: 'Helvetica-Bold',
    lineHeight: 1.25,
  },
  entryTitleInRow: {
    flex: 1,
  },
  entryMeta: {
    fontSize: 8,
    color: '#4B5563',
    textAlign: 'right',
  },
  entrySubheading: {
    fontSize: 8.5,
    fontFamily: 'Helvetica-Bold',
    marginBottom: 2,
  },
  body: {
    fontSize: 8.5,
    lineHeight: 1.35,
  },
  bulletRow: {
    flexDirection: 'row',
    marginBottom: 2,
    paddingLeft: 3,
  },
  bullet: {
    width: 9,
    fontSize: 8.5,
  },
  bulletText: {
    flex: 1,
    fontSize: 8.5,
    lineHeight: 1.35,
  },
});

const toText = (value) => {
  if (value == null) return '';
  if (Array.isArray(value)) {
    return value.map((item) => {
      if (typeof item === 'string' || typeof item === 'number') return String(item);
      if (item && typeof item === 'object') {
        const name = item.name || item.language || '';
        const level = item.proficiency || item.level || '';
        return [name, level && `(${level})`].filter(Boolean).join(' ');
      }
      return '';
    }).filter(Boolean).join(', ');
  }
  if (typeof value === 'object') return Object.values(value).filter(Boolean).join(', ');
  return String(value);
};

const hasContent = (value) => {
  if (value == null) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  if (Array.isArray(value)) return value.some(hasContent);
  if (typeof value === 'object') return Object.values(value).some(hasContent);
  return Boolean(value);
};

const renderBulletList = (items) => {
  const values = Array.isArray(items) ? items : [items];
  return values.filter(Boolean).map((item, index) => (
    <View key={index} style={styles.bulletRow}>
      <Text style={styles.bullet}>•</Text>
      <Text style={styles.bulletText}>{toText(item)}</Text>
    </View>
  ));
};

const renderTextSection = (title, content) => {
  if (!hasContent(content)) return null;
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {Array.isArray(content) ? renderBulletList(content) : <Text style={styles.body}>{toText(content)}</Text>}
    </View>
  );
};

const ResumeWordedPDFTemplate = ({ resumeData }) => {
  if (!resumeData) return null;

  if (typeof resumeData === 'string') {
    return (
      <Document>
        <Page size="A4" style={styles.page}>
          <Text style={styles.body}>{resumeData}</Text>
        </Page>
      </Document>
    );
  }

  const {
    name, email, phone, linkedin, github, website, summary,
    experience, education, certifications, trainings, skills, projects, languages,
  } = resumeData;
  const contact = [email, phone, linkedin, github, website].filter(Boolean).join(' | ');

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.name}>{toText(name)}</Text>
          {contact ? <Text style={styles.contact}>{contact}</Text> : null}
        </View>

        {renderTextSection('Professional Summary', summary)}

        {hasContent(experience) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Professional Experience</Text>
            {Array.isArray(experience) ? experience.map((item, index) => {
              if (typeof item === 'string') {
                return <View key={index} style={styles.entry}>{renderBulletList(item)}</View>;
              }
              const role = item.role || item.title;
              return (
                <View key={index} style={styles.entry}>
                  {(item.company || item.location) ? (
                    <View style={styles.entryHeading}>
                      <Text style={[styles.entryTitle, styles.entryTitleInRow]}>{toText(item.company)}</Text>
                      {item.location ? <Text style={styles.entryMeta}>{toText(item.location)}</Text> : null}
                    </View>
                  ) : null}
                  {(role || item.duration) ? (
                    <View style={styles.entryHeading}>
                      {role ? <Text style={styles.entrySubheading}>{toText(role)}</Text> : <Text />}
                      {item.duration ? <Text style={styles.entryMeta}>{toText(item.duration)}</Text> : null}
                    </View>
                  ) : null}
                  {item.responsibilities ? renderBulletList(item.responsibilities) : null}
                  {item.skills ? (
                    <Text style={styles.body}>Skills: {toText(item.skills)}</Text>
                  ) : null}
                </View>
              );
            }) : <Text style={styles.body}>{toText(experience)}</Text>}
          </View>
        )}

        {hasContent(education) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Education</Text>
            {Array.isArray(education) ? education.map((item, index) => {
              if (typeof item === 'string') {
                return <View key={index} style={styles.entry}>{renderBulletList(item)}</View>;
              }
              return (
                <View key={index} style={styles.entry}>
                  {(item.institution || item.location) ? (
                    <View style={styles.entryHeading}>
                      <Text style={[styles.entryTitle, styles.entryTitleInRow]}>{toText(item.institution)}</Text>
                      {item.location ? <Text style={styles.entryMeta}>{toText(item.location)}</Text> : null}
                    </View>
                  ) : null}
                  {(item.degree || item.title || item.duration) ? (
                    <View style={styles.entryHeading}>
                      <Text style={styles.body}>{toText(item.degree || item.title)}</Text>
                      {item.duration ? <Text style={styles.entryMeta}>{toText(item.duration)}</Text> : null}
                    </View>
                  ) : null}
                </View>
              );
            }) : <Text style={styles.body}>{toText(education)}</Text>}
          </View>
        )}

        {hasContent(projects) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Projects</Text>
            {Array.isArray(projects) ? projects.map((item, index) => {
              if (typeof item === 'string') {
                return <View key={index} style={styles.entry}>{renderBulletList(item)}</View>;
              }
              const details = item.description || [];
              return (
                <View key={index} style={styles.entry}>
                  <Text style={styles.entryTitle}>{item.name || item.title}</Text>
                  {renderBulletList(details)}
                  {(item.technologies || item.skills) ? (
                    <Text style={styles.body}>Skills: {toText(item.technologies || item.skills)}</Text>
                  ) : null}
                </View>
              );
            }) : <Text style={styles.body}>{toText(projects)}</Text>}
          </View>
        )}

        {[skills, languages, certifications, trainings].some(hasContent) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Additional Information</Text>
            {hasContent(skills) ? <Text style={styles.body}>Technical Skills: {toText(skills)}</Text> : null}
            {hasContent(languages) ? <Text style={styles.body}>Languages: {toText(languages)}</Text> : null}
            {hasContent(certifications) ? <Text style={styles.body}>Certifications: {toText(certifications)}</Text> : null}
            {hasContent(trainings) ? <Text style={styles.body}>Training: {toText(trainings)}</Text> : null}
          </View>
        )}
      </Page>
    </Document>
  );
};

export default ResumeWordedPDFTemplate;
