import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database.mongodb_handler import MongoDBHandler
import base64
import os

def dashboard_page(db_handler: MongoDBHandler = None):
    # Load and encode the cat frame images (1.png to 6.png)
    assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    cat_frames = []
    
    try:
        for i in range(1, 7):
            frame_path = os.path.join(assets_path, f"{i}.png")
            with open(frame_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                cat_frames.append(f"data:image/png;base64,{encoded_string}")
    except Exception as e:
        st.warning(f"Cat frame images not found in: {assets_path}")
        cat_frames = []
    
    # Add animated header with running cat frames
    if cat_frames:
        st.markdown(f"""
    <style>
    .animation-container {{
        position: relative;
        height: 150px;
        width: 100%;
        margin-bottom: 20px;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(196,240,237,0.1) 0%, rgba(255,255,255,0) 100%);
        border-radius: 10px;
    }}
    
    .running-cat {{
        position: absolute;
        bottom: 20px;
        width: 150px;
        height: 150px;
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        animation: moveCat 12s linear infinite;
    }}
    
    @keyframes runCatFrames {{
        0%, 16.66% {{
            background-image: url('{cat_frames[0]}');
        }}
        16.67%, 33.32% {{
            background-image: url('{cat_frames[1]}');
        }}
        33.33%, 49.98% {{
            background-image: url('{cat_frames[2]}');
        }}
        49.99%, 66.64% {{
            background-image: url('{cat_frames[3]}');
        }}
        66.65%, 83.30% {{
            background-image: url('{cat_frames[4]}');
        }}
        83.31%, 100% {{
            background-image: url('{cat_frames[5]}');
        }}
    }}
    
    .running-cat {{
        animation: runCatFrames 0.6s infinite, moveCat 12s linear infinite;
    }}
    
    @keyframes moveCat {{
        0% {{
            left: -150px;
            transform: scaleX(1);
        }}
        48% {{
            left: 100%;
            transform: scaleX(1);
        }}
        50% {{
            left: 100%;
            transform: scaleX(-1);
        }}
        98% {{
            left: -150px;
            transform: scaleX(-1);
        }}
        100% {{
            left: -150px;
            transform: scaleX(1);
        }}
    }}
    
    .paw-print {{
        position: absolute;
        bottom: 30px;
        font-size: 20px;
        opacity: 0;
        animation: fadePaw 12s linear infinite;
    }}
    
    @keyframes fadePaw {{
        0% {{
            opacity: 0;
            transform: scale(0.8);
        }}
        5% {{
            opacity: 0.5;
            transform: scale(1);
        }}
        15% {{
            opacity: 0.3;
        }}
        25% {{
            opacity: 0;
            transform: scale(0.8);
        }}
        100% {{
            opacity: 0;
        }}
    }}
    </style>
    <div class="animation-container">
        <div class="running-cat"></div>
        <div class="paw-print" style="left: 5%; animation-delay: 0.3s;">🐾</div>
        <div class="paw-print" style="left: 10%; animation-delay: 0.6s;">🐾</div>
        <div class="paw-print" style="left: 15%; animation-delay: 0.9s;">🐾</div>
        <div class="paw-print" style="left: 20%; animation-delay: 1.2s;">🐾</div>
        <div class="paw-print" style="left: 25%; animation-delay: 1.5s;">🐾</div>
        <div class="paw-print" style="left: 30%; animation-delay: 1.8s;">🐾</div>
        <div class="paw-print" style="left: 35%; animation-delay: 2.1s;">🐾</div>
        <div class="paw-print" style="left: 40%; animation-delay: 2.4s;">🐾</div>
        <div class="paw-print" style="left: 45%; animation-delay: 2.7s;">🐾</div>
        <div class="paw-print" style="left: 50%; animation-delay: 3.0s;">🐾</div>
        <div class="paw-print" style="left: 55%; animation-delay: 3.3s;">🐾</div>
        <div class="paw-print" style="left: 60%; animation-delay: 3.6s;">🐾</div>
        <div class="paw-print" style="left: 65%; animation-delay: 3.9s;">🐾</div>
        <div class="paw-print" style="left: 70%; animation-delay: 4.2s;">🐾</div>
        <div class="paw-print" style="left: 75%; animation-delay: 4.5s;">🐾</div>
        <div class="paw-print" style="left: 80%; animation-delay: 4.8s;">🐾</div>
        <div class="paw-print" style="left: 85%; animation-delay: 5.1s;">🐾</div>
        <div class="paw-print" style="left: 90%; animation-delay: 5.4s;">🐾</div>
        <div class="paw-print" style="left: 95%; animation-delay: 5.7s;">🐾</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("#  The Listening Post")
    st.markdown(f"### Welcome back, {st.session_state.get('username', 'User')}! 👋")
    st.markdown("---")
    
    # Get user ID from session
    user_id = st.session_state.get('user_id')
    
    # Initialize session state for tracking
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    # Cache dashboard data in session state to avoid refetching
    cache_key = f"dashboard_data_{user_id}"
    cache_time_key = f"dashboard_time_{user_id}"
    current_time = datetime.now()
    
    # Refresh cache every 30 seconds
    should_refresh = (
        cache_key not in st.session_state or 
        cache_time_key not in st.session_state or
        (current_time - st.session_state[cache_time_key]).total_seconds() > 30
    )
    
    if should_refresh and db_handler and user_id:
        st.session_state[cache_key] = {
            'user_stats': db_handler.get_user_statistics(user_id),
            'user_history': db_handler.get_user_analysis_history(user_id, limit=30),
            'dashboard_data': db_handler.get_dashboard_data(user_id)
        }
        st.session_state[cache_time_key] = current_time
    
    # Use cached data
    if cache_key in st.session_state:
        cached = st.session_state[cache_key]
        user_stats = cached['user_stats']
        user_history = cached['user_history']
        dashboard_data = cached['dashboard_data']
    else:
        user_stats = {'total_analyses': 0, 'recent_analyses': 0, 'analysis_by_type': {}}
        user_history = []
        dashboard_data = None
    
    # Top Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics from user data
    total_analyses = user_stats.get('total_analyses', 0)
    recent_analyses = user_stats.get('recent_analyses', 0)
    
    # Calculate average wellness score from history (0-100 scale)
    if user_history:
        wellness_scores = [item['data'].get('wellness_score', 0) for item in user_history if 'wellness_score' in item.get('data', {})]
        avg_score = round(np.mean(wellness_scores), 1) if wellness_scores else 0
    else:
        avg_score = 0
    
    with col1:
        display_score = f"{avg_score:.1f}" if avg_score > 0 else "--"
        wellness_text = 'Excellent Wellness' if avg_score > 80 else 'Good Wellness' if avg_score > 60 else 'Moderate Wellness' if avg_score > 40 else 'Start analyzing to track' if avg_score == 0 else 'Needs Attention'
        st.markdown(f"""
        <div class="custom-card">
            <h4 style="color: #000000; margin: 0;">Overall Wellness Score</h4>
            <h2 style="color: #000000; margin: 10px 0;">{display_score}/100</h2>
            <p style="color: #000000; margin: 0;">{wellness_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        stress_level = "Low" if avg_score > 70 else "Medium" if avg_score > 50 else "Not available" if avg_score == 0 else "High"
        st.markdown(f"""
        <div class="custom-card">
            <h4 style="color: #000000; margin: 0;">Stress Level</h4>
            <h2 style="color: #000000; margin: 10px 0;">{stress_level}</h2>
            <p style="color: #000000; margin: 0;">{'Based on recent analyses' if avg_score > 0 else 'Perform analyses to see'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="custom-card">
            <h4 style="color: #000000; margin: 0;">Analyses Done</h4>
            <h2 style="color: #000000; margin: 10px 0;">{total_analyses}</h2>
            <p style="color: #000000; margin: 0;">Total analyses</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="custom-card">
            <h4 style="color: #000000; margin: 0;">Check-ins</h4>
            <h2 style="color: #000000; margin: 10px 0;">{recent_analyses}</h2>
            <p style="color: #000000; margin: 0;">Last 30 days</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Dashboard Content
    tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Insights", "History", "Recommendations"])
    
    with tab1:
        st.markdown("### Emotional Wellness Trends")
        
        if user_history and len(user_history) > 0:
            # Use real user data
            df_history = pd.DataFrame(user_history)
            df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
            df_history = df_history.sort_values('timestamp')
            
            # Extract wellness scores
            wellness_data = []
            for item in user_history:
                wellness_data.append({
                    'date': pd.to_datetime(item['timestamp']),
                    'wellness': item['data'].get('wellness_score', 0),
                    'type': item['analysis_type']
                })
            
            df_wellness = pd.DataFrame(wellness_data).sort_values('date')
            
            # Create line chart with real data
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_wellness['date'], 
                y=df_wellness['wellness'],
                name='Wellness Score',
                line=dict(color='#c4f0ed', width=3),
                mode='lines+markers',
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title='Your Wellness Journey',
                xaxis_title='Date',
                yaxis_title='Wellness Score',
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400,
                font=dict(family='Inter, sans-serif')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analysis type distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Analysis Type Distribution")
                analysis_counts = user_stats.get('analysis_by_type', {})
                
                if analysis_counts:
                    labels = [k.replace('_', ' ').title() for k in analysis_counts.keys()]
                    values = list(analysis_counts.values())
                    colors = ['#c4f0ed', '#a8e4e0', '#8cd9d4', '#70cec8', '#54c3bc']
                    
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        marker=dict(colors=colors[:len(labels)]),
                        hole=0.4
                    )])
                    
                    fig_pie.update_layout(
                        showlegend=True,
                        height=300,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#000000')
                    )
                    
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Perform different types of analyses to see distribution")
            
            with col2:
                st.markdown("#### Recent Activity")
                st.markdown(f"""
                <div class="custom-card">
                    <p style="color: #000000;"><strong>Total Analyses:</strong> {total_analyses}</p>
                    <p style="color: #000000;"><strong>Last 30 Days:</strong> {recent_analyses}</p>
                    <p style="color: #000000;"><strong>Average Score:</strong> {avg_score}/100</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Show message for new users
            st.info(" Welcome! Start analyzing your mental health to see your wellness trends here.")
            st.markdown("""
            <div class="custom-card">
                <h4>Get Started:</h4>
                <ul style="color: #000000; line-height: 1.8;">
                    <li> Go to <strong>Text Analysis</strong> to analyze your written thoughts</li>
                    <li> Try <strong>Voice Analysis</strong> to detect emotions from speech</li>
                    <li> Use <strong>Facial Analysis</strong> to analyze facial expressions</li>
                </ul>
                <p style="color: #666; margin-top: 20px;">
                    Your analysis history will appear here once you start tracking your mental wellness journey.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Personalized Insights")
        
        if user_history and len(user_history) > 0:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Generate real insights based on user data
                sentiments = [item['data'].get('sentiment', 'Unknown') for item in user_history if 'sentiment' in item.get('data', {})]
                positive_count = sentiments.count('Positive')
                negative_count = sentiments.count('Negative')
                neutral_count = sentiments.count('Neutral')
                
                st.markdown(f"""
                <div class="custom-card">
                    <h4>Key Observations</h4>
                    <ul style="color: #000000; line-height: 1.8;">
                        <li>You have completed {total_analyses} mental health analyses</li>
                        <li>Your average wellness score is {avg_score}/100</li>
                        <li>Sentiment breakdown: {positive_count} positive, {neutral_count} neutral, {negative_count} negative</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="custom-card" style="margin-top: 20px;">
                    <h4>Wellness Progress</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Show actual progress
                st.markdown(f"**Current Wellness Score**: {avg_score}%")
                st.progress(avg_score / 100 if avg_score > 0 else 0)
                st.markdown("<br>", unsafe_allow_html=True)
            
            with col2:
                risk_level = "Low Risk" if avg_score > 80 else "Moderate Risk" if avg_score > 60 else "Needs Attention"
                risk_class = "risk-low" if avg_score > 80 else "risk-moderate" if avg_score > 60 else "risk-high"
                
                st.markdown(f"""
                <div class="custom-card">
                    <h4 style="color: #c4f0ed;">Current Status</h4>
                    <div class="{risk_class} risk-badge">
                        {risk_level}
                    </div>
                    <p style="margin-top: 20px; color: #000000;">
                        {'Keep up the great work! Your mental wellness is strong.' if avg_score > 80 else
                         'Your mental wellness is in the moderate range. Some areas need attention.' if avg_score > 60 else
                         'Consider reaching out to a mental health professional for support.'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Recent alerts
                if recent_analyses > 0:
                    st.markdown(f"""
                    <div class="custom-card" style="margin-top: 20px;">
                        <h4 style="color: #c4f0ed;">Activity</h4>
                        <div style="background: #e8f9ec; padding: 10px; border-radius: 8px;">
                            <strong>✓ Active User</strong><br>
                            <small>{recent_analyses} check-ins in last 30 days</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Insights will appear here once you complete your first analysis.")
            st.markdown("""
            <div class="custom-card">
                <h4>What You'll See Here:</h4>
                <ul style="color: #000000; line-height: 1.8;">
                    <li><strong>Key Observations:</strong> Patterns in your mental health data</li>
                    <li><strong>Wellness Breakdown:</strong> Detailed scores across different areas</li>
                    <li><strong>Current Status:</strong> Your overall risk level and recommendations</li>
                    <li><strong>Alerts:</strong> Important trends and changes to be aware of</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("###  Analysis History")
        
        if user_history:
            # Convert history to DataFrame
            history_data = pd.DataFrame([{
                'Date': item['timestamp'],
                'Type': item['analysis_type'].replace('_', ' ').title(),
                'Score': item['data'].get('wellness_score', item['data'].get('score', 0)),
                'Sentiment': item['data'].get('sentiment', item['data'].get('emotion', 'N/A')),
                'Risk Level': item['data'].get('risk_level', 'Unknown')
            } for item in user_history])
            
            st.dataframe(
                history_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Date': st.column_config.TextColumn('Date & Time'),
                    'Type': st.column_config.TextColumn('Analysis Type'),
                    'Score': st.column_config.ProgressColumn('Wellness Score', min_value=0, max_value=100),
                    'Sentiment': st.column_config.TextColumn('Sentiment/Emotion'),
                    'Risk Level': st.column_config.TextColumn('Risk Level')
                }
            )
            
            # Export option
            st.download_button(
                label=" Download History (CSV)",
                data=history_data.to_csv(index=False).encode('utf-8'),
                file_name=f'mental_health_history_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv'
            )
        else:
            st.info("No analysis history yet. Start analyzing to see your history!")
    
    with tab4:
        st.markdown("###  Personalized Recommendations")
        
        if user_history and len(user_history) > 0:
            # Generate recommendations based on wellness score (low score = high risk)
            # avg_score is already calculated above from wellness_scores
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="custom-card">
                    <h4>Personalized Tips</h4>
                    <p style="color: #000000; line-height: 1.8;">
                        Based on your analyses, here are some recommendations:
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show recommendations based on wellness score (low score = high risk)
                if avg_score < 40:
                    st.markdown("""
                    <div class="custom-card" style="margin-top: 20px;">
                        <h4> Action Items</h4>
                        <div style="background: #fff4e5; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ff6b6b;">
                            <strong>High Priority</strong><br>
                            Consider scheduling an appointment with a mental health professional
                        </div>
                        <div style="background: #e8f9ec; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #c4f0ed;">
                            <strong>Self-Care</strong><br>
                            Practice daily stress-reduction techniques like meditation or deep breathing
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif avg_score < 60:
                    st.markdown("""
                    <div class="custom-card" style="margin-top: 20px;">
                        <h4> Action Items</h4>
                        <div style="background: #e8f9ec; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #c4f0ed;">
                            <strong>Maintain Balance</strong><br>
                            Continue your current wellness practices
                        </div>
                        <div style="background: #e8f9ec; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #a8e4e0;">
                            <strong>Growth</strong><br>
                            Explore new stress management techniques
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="custom-card" style="margin-top: 20px;">
                        <h4> Keep It Up!</h4>
                        <div style="background: #d4f4dd; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4caf50;">
                            <strong>Great Work</strong><br>
                            Your mental wellness is strong. Keep maintaining healthy habits!
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="custom-card">
                    <h4> Resources</h4>
                    <ul style="color: #000000; line-height: 1.8;">
                        <li><a href="https://www.headspace.com" target="_blank" style="color: #2c7a7b; text-decoration: none;">Headspace - Meditation & Sleep</a></li>
                        <li><a href="https://www.calm.com" target="_blank" style="color: #2c7a7b; text-decoration: none;">Calm - Mental Fitness</a></li>
                        <li><a href="https://www.betterhelp.com" target="_blank" style="color: #2c7a7b; text-decoration: none;">BetterHelp - Online Therapy</a></li>
                        <li><a href="https://www.talkspace.com" target="_blank" style="color: #2c7a7b; text-decoration: none;">Talkspace - Online Counseling</a></li>
                        <li><a href="https://www.psychologytoday.com/us/therapists" target="_blank" style="color: #2c7a7b; text-decoration: none;">Find a Therapist Near You</a></li>
                        <li><a href="https://www.mentalhealth.gov" target="_blank" style="color: #2c7a7b; text-decoration: none;">MentalHealth.gov</a></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="custom-card" style="margin-top: 20px;">
                    <h4> Crisis Resources</h4>
                    <p style="color: #000000; line-height: 1.8;">
                        <strong>National Suicide Prevention Lifeline:</strong><br>
                         <a href="tel:1-800-273-8255" style="color: #2c7a7b; text-decoration: none;">1-800-273-8255</a><br><br>
                        <strong>Crisis Text Line:</strong><br>
                         Text HOME to <strong>741741</strong><br><br>
                        <strong>Emergency:</strong><br>
                         Call <a href="tel:911" style="color: #2c7a7b; text-decoration: none;">911</a>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # For new users without analysis data
            st.info(" Personalized recommendations will appear here based on your analysis results.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="custom-card">
                    <h4> What You'll Get:</h4>
                    <ul style="color: #000000; line-height: 1.8;">
                        <li><strong>Personalized Tips:</strong> Custom advice based on your wellness data</li>
                        <li><strong>Action Items:</strong> Prioritized recommendations for improvement</li>
                        <li><strong>Progress Tracking:</strong> See how recommendations align with your journey</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="custom-card">
                    <h4> Resources</h4>
                    <ul style="color: #000000; line-height: 1.8;">
                        <li><a href="https://www.headspace.com" target="_blank" style="color: #2c7a7b; text-decoration: none;">Headspace - Meditation & Sleep</a></li>
                        <li><a href="https://www.calm.com" target="_blank" style="color: #2c7a7b; text-decoration: none;">Calm - Mental Fitness</a></li>
                        <li><a href="https://www.betterhelp.com" target="_blank" style="color: #2c7a7b; text-decoration: none;">BetterHelp - Online Therapy</a></li>
                        <li><a href="https://www.talkspace.com" target="_blank" style="color: #2c7a7b; text-decoration: none;">Talkspace - Online Counseling</a></li>
                        <li><a href="https://www.psychologytoday.com/us/therapists" target="_blank" style="color: #2c7a7b; text-decoration: none;">Find a Therapist Near You</a></li>
                        <li><a href="https://www.mentalhealth.gov" target="_blank" style="color: #2c7a7b; text-decoration: none;">MentalHealth.gov</a></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="custom-card" style="margin-top: 20px;">
                    <h4> Crisis Resources</h4>
                    <p style="color: #000000; line-height: 1.8;">
                        <strong>National Suicide Prevention Lifeline:</strong><br>
                         <a href="tel:1-800-273-8255" style="color: #2c7a7b; text-decoration: none;">1-800-273-8255</a><br><br>
                        <strong>Crisis Text Line:</strong><br>
                         Text HOME to <strong>741741</strong><br><br>
                        <strong>Emergency:</strong><br>
                         Call <a href="tel:911" style="color: #2c7a7b; text-decoration: none;">911</a>
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #999; padding: 20px;'>
        <p> <strong>Disclaimer:</strong> This tool is for informational purposes only and does not replace professional medical advice.</p>
        <p>If you're experiencing a mental health crisis, please contact a healthcare professional immediately.</p>
    </div>
    """, unsafe_allow_html=True)
