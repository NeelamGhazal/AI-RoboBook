import React from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function Home() {
  const {siteConfig} = useDocusaurusContext();

  return (
    <Layout
      title={siteConfig.title}
      description="Physical AI & Humanoid Robotics Curriculum">
      <main>
        {/* Hero Section */}
        <section className={styles.heroSection}>
          <div className={styles.heroGrid}>
            {/* Hero Image - LEFT */}
            <div className={styles.heroImage}>
              <img
                src={useBaseUrl('/img/hero.jpg')}
                alt="Humanoid Robot"
                className={styles.heroImageImg}
              />
            </div>

            {/* Hero Content - RIGHT */}
            <div className={styles.heroContent}>
              <div className={styles.heroBadge}>
                Graduate-Level Curriculum
              </div>
              <h1 className={styles.heroTitle}>
                Physical AI & Humanoid Robotics
              </h1>
              <p className={styles.heroDescription}>
                Learn to control physical androids using ROS 2, advanced vision systems, large language models, and reinforcement learning with this free, open-source textbook.
              </p>
              <Link
                className={`${styles.heroCTAButton} button button--primary button--lg`}
                to="/docs/intro">
                Start Learning
              </Link>
            </div>
          </div>
        </section>

        {/* What's Inside Section */}
        <section className={styles.featuresSection}>
          <div className={styles.featuresHeader}>
            <div className={styles.featuresBadge}>What's Inside the Book</div>
            <h2 className={styles.featuresTitle}>What's Inside the Book</h2>
            <p className={styles.featuresDescription}>
              Everything you need to master robotics from fundamentals to advanced applications
            </p>
          </div>

          <div className={styles.featuresGrid}>
            {/* Feature Card 1: ROS 2 */}
            <div className={styles.featureCard}>
              <div className={styles.featureCardIcon}>
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 2v20M2 12h20"/>
                </svg>
              </div>
              <h3 className={styles.featureCardTitle}>ROS 2 Integration</h3>
              <p className={styles.featureCardDescription}>
                Master the Robot Operating System 2 architecture, nodes, topics, services, and build real-world applications.
              </p>
            </div>

            {/* Feature Card 2: Vision */}
            <div className={styles.featureCard}>
              <div className={styles.featureCardIcon}>
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </div>
              <h3 className={styles.featureCardTitle}>Advanced Vision Systems</h3>
              <p className={styles.featureCardDescription}>
                Computer vision, depth sensing, object detection, and visual SLAM for autonomous navigation.
              </p>
            </div>

            {/* Feature Card 3: LLM */}
            <div className={styles.featureCard}>
              <div className={styles.featureCardIcon}>
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <h3 className={styles.featureCardTitle}>Large Language Models</h3>
              <p className={styles.featureCardDescription}>
                Integrate OpenAI Whisper, GPT, and natural language processing for human-robot interaction.
              </p>
            </div>

            {/* Feature Card 4: RL */}
            <div className={styles.featureCard}>
              <div className={styles.featureCardIcon}>
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </div>
              <h3 className={styles.featureCardTitle}>Reinforcement Learning</h3>
              <p className={styles.featureCardDescription}>
                Train robots using RL algorithms, simulation environments, and real-world deployment strategies.
              </p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className={styles.ctaSection}>
          <div className={styles.ctaBadge}>Start Your Journey Today</div>
          <h2 className={styles.ctaTitle}>Ready to Start Your Robotics Journey?</h2>
          <p className={styles.ctaDescription}>
            Access comprehensive documentation, interactive examples, and step-by-step guides to master robotics concepts and build amazing projects.
          </p>
          <Link
            className={`${styles.ctaButton} button button--primary button--lg`}
            to="/docs/intro">
            Start Learning Now
          </Link>
        </section>

        {/* Book Content Section - Module Cards */}
        <section className={styles.modulesSection}>
          <div className={styles.modulesSectionHeader}>
            <h2 className={styles.modulesSectionTitle}>Course Modules</h2>
            <div className={styles.modulesTopButtons}>
              <button className={styles.btnPersonalizedMode}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                Personalized Mode
              </button>
              <button className={styles.btnLanguageToggle}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="2" y1="12" x2="22" y2="12"/>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                </svg>
                English / اردو
              </button>
            </div>
          </div>

          <div className={styles.modulesGrid}>
            {/* Module 1 */}
            <div className={styles.moduleCard}>
              <div className={styles.moduleCardNumber}>Module 1</div>
              <h3 className={styles.moduleCardTitle}>ROS 2 Fundamentals</h3>
              <p className={styles.moduleCardDescription}>
                Learn the Robot Operating System 2 architecture, nodes, topics, services, and create your first ROS 2 node.
              </p>
              <ul className={styles.moduleCardTopics}>
                <li>ROS 2 Architecture & Core Concepts</li>
                <li>Nodes, Topics & Services</li>
                <li>Launch Files & Parameters</li>
                <li>Hands-on Project: First ROS 2 Node</li>
              </ul>
              <Link
                className={`${styles.moduleCardButton} button button--secondary`}
                to="/docs/module1/chapter1">
                Start Module 1 →
              </Link>
            </div>

            {/* Module 2 */}
            <div className={styles.moduleCard}>
              <div className={styles.moduleCardNumber}>Module 2</div>
              <h3 className={styles.moduleCardTitle}>Simulation (Gazebo/Unity)</h3>
              <p className={styles.moduleCardDescription}>
                Master physics simulation fundamentals, Gazebo setup, URDF/SDF formats, and Unity integration for robotics.
              </p>
              <ul className={styles.moduleCardTopics}>
                <li>Gazebo Simulation Environment</li>
                <li>URDF/SDF Robot Models</li>
                <li>Unity Integration for Robotics</li>
                <li>Hands-on Project: Simulated Robot</li>
              </ul>
              <Link
                className={`${styles.moduleCardButton} button button--secondary`}
                to="/docs/module2/chapter1">
                Start Module 2 →
              </Link>
            </div>

            {/* Module 3 */}
            <div className={styles.moduleCard}>
              <div className={styles.moduleCardNumber}>Module 3</div>
              <h3 className={styles.moduleCardTitle}>NVIDIA Isaac</h3>
              <p className={styles.moduleCardDescription}>
                Explore Isaac Sim, Isaac ROS perception, Nav2 path planning, and synthetic data generation.
              </p>
              <ul className={styles.moduleCardTopics}>
                <li>Isaac Sim Advanced Simulation</li>
                <li>Isaac ROS Perception Pipeline</li>
                <li>Nav2 Path Planning & VSLAM</li>
                <li>Hands-on Project: Autonomous Navigation</li>
              </ul>
              <Link
                className={`${styles.moduleCardButton} button button--secondary`}
                to="/docs/module3/chapter1">
                Start Module 3 →
              </Link>
            </div>

            {/* Module 4 */}
            <div className={styles.moduleCard}>
              <div className={styles.moduleCardNumber}>Module 4</div>
              <h3 className={styles.moduleCardTitle}>Voice Control & LLM Integration</h3>
              <p className={styles.moduleCardDescription}>
                Integrate OpenAI Whisper, LLM cognitive planning, NLP processing, and multi-modal interaction.
              </p>
              <ul className={styles.moduleCardTopics}>
                <li>OpenAI Whisper Voice Recognition</li>
                <li>LLM Integration & Cognitive Planning</li>
                <li>Natural Language Processing</li>
                <li>Hands-on Project: Voice-Controlled Robot</li>
              </ul>
              <Link
                className={`${styles.moduleCardButton} button button--secondary`}
                to="/docs/module4/chapter1">
                Start Module 4 →
              </Link>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
