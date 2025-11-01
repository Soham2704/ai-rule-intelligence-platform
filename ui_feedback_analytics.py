"""
Streamlit UI Component: Feedback Analytics Dashboard
-----------------------------------------------------
Visualizes the adaptive feedback system in real-time
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from adaptive_feedback_system import AdaptiveFeedbackSystem
from datetime import datetime, timedelta
import json


def render_feedback_analytics():
    """Main render function for feedback analytics page"""
    
    st.title("🔄 Adaptive Feedback Analytics")
    st.markdown("Real-time visualization of the city-adaptive learning system")
    
    # Initialize system
    system = AdaptiveFeedbackSystem()
    
    # Get comprehensive report
    report = system.generate_feedback_report()
    
    # === SECTION 1: Overall Statistics ===
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Feedback",
            report["total_feedback_count"],
            delta="+12 (24h)" if report["total_feedback_count"] > 50 else None
        )
    
    with col2:
        approval_rate = report["overall_approval_rate"]
        st.metric(
            "Overall Approval Rate",
            f"{approval_rate:.1%}",
            delta=f"+{(approval_rate-0.75)*100:.1f}%" if approval_rate > 0.75 else None
        )
    
    with col3:
        st.metric(
            "Cities Tracked",
            report["cities_tracked"]
        )
    
    with col4:
        st.metric(
            "System Status",
            report["system_status"],
            delta="✅ Active" if report["system_status"] == "Active" else "⏳ Learning"
        )
    
    st.divider()
    
    # === SECTION 2: City-by-City Breakdown ===
    st.header("🏙️ City-Specific Performance")
    
    # Create dataframe from city breakdown
    city_data = []
    for city_stat in report["city_breakdown"]:
        city_data.append({
            "City": city_stat["city"],
            "Cases": city_stat["total_cases"],
            "Approval Rate": f"{city_stat['approval_rate']:.1%}",
            "Positive": city_stat.get("positive_feedback", 0),
            "Negative": city_stat.get("negative_feedback", 0),
            "Confidence Multiplier": f"{city_stat['confidence_multiplier']:.2f}x",
            "Status": city_stat["status"]
        })
    
    if city_data:
        df = pd.DataFrame(city_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # === SECTION 3: Visualizations ===
        st.header("📈 Performance Visualization")
        
        # Chart 1: Approval Rates by City
        fig_approval = px.bar(
            df,
            x="City",
            y="Approval Rate",
            title="Approval Rates by City",
            color="Approval Rate",
            color_continuous_scale="RdYlGn"
        )
        fig_approval.update_traces(texttemplate='%{y}', textposition='outside')
        st.plotly_chart(fig_approval, use_container_width=True)
        
        # Chart 2: Feedback Volume by City
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Bar(
            name='Positive',
            x=df["City"],
            y=df["Positive"],
            marker_color='green'
        ))
        fig_volume.add_trace(go.Bar(
            name='Negative',
            x=df["City"],
            y=df["Negative"],
            marker_color='red'
        ))
        fig_volume.update_layout(
            title="Feedback Volume by City",
            barmode='stack',
            xaxis_title="City",
            yaxis_title="Feedback Count"
        )
        st.plotly_chart(fig_volume, use_container_width=True)
        
        # === SECTION 4: Reward Weights Visualization ===
        st.header("⚖️ City-Adaptive Reward Weights")
        
        # Show weights for each city
        for city_stat in report["city_breakdown"]:
            if city_stat["total_cases"] > 0:
                with st.expander(f"📍 {city_stat['city']} - {city_stat['total_cases']} cases analyzed"):
                    weights = city_stat["action_weights"]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Weight bars
                        weight_df = pd.DataFrame({
                            "Action": ["Low FSI", "Medium FSI", "High FSI"],
                            "Weight": weights
                        })
                        
                        fig_weights = px.bar(
                            weight_df,
                            x="Action",
                            y="Weight",
                            title=f"{city_stat['city']} Action Weights",
                            color="Weight",
                            color_continuous_scale="Blues",
                            range_y=[0, 2.0]
                        )
                        fig_weights.add_hline(y=1.0, line_dash="dash", line_color="gray",
                                             annotation_text="Baseline (1.0)")
                        st.plotly_chart(fig_weights, use_container_width=True)
                    
                    with col2:
                        # Stats
                        st.metric("Approval Rate", f"{city_stat['approval_rate']:.1%}")
                        st.metric("Confidence Multiplier", f"{city_stat['confidence_multiplier']:.2f}x")
                        st.metric("Status", city_stat["status"])
                        
                        # Interpretation
                        if city_stat["approval_rate"] >= 0.85:
                            st.success("✅ High confidence - system performing well")
                        elif city_stat["approval_rate"] >= 0.70:
                            st.info("ℹ️ Moderate confidence - standard performance")
                        else:
                            st.warning("⚠️ Low confidence - needs more learning data")
    
    else:
        st.info("No feedback data available yet. Start analyzing cases to build the dataset!")
    
    st.divider()
    
    # === SECTION 5: Recent Feedback Timeline ===
    st.header("📅 Recent Feedback Activity")
    
    if report.get("recent_feedback"):
        # Show last 10 feedback events
        for fb in reversed(report["recent_feedback"][-10:]):
            emoji = "👍" if fb["feedback_type"] == "up" else "👎"
            delta_emoji = "📈" if fb["weight_change"] > 0 else "📉"
            
            st.markdown(f"""
            **{emoji} {fb['city']}** - `{fb['case_id']}`  
            *{fb['timestamp']}*  
            {delta_emoji} Weight change: {fb['weight_change']:+.3f} | Approval: {fb['approval_rate']:.1%}
            """)
            st.divider()
    else:
        st.info("No recent feedback activity")
    
    # === SECTION 6: System Configuration ===
    with st.expander("🔧 System Configuration"):
        st.json({
            "reward_table_path": system.reward_table_path,
            "cities_configured": list(system.reward_weights.keys()),
            "total_weight_updates": len(system.feedback_history),
            "database_status": "Connected" if system.db else "Disconnected"
        })
    
    # === SECTION 7: Confidence Adjustment Calculator ===
    st.header("🧮 Confidence Adjustment Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        test_city = st.selectbox(
            "Select City",
            options=[city["city"] for city in report["city_breakdown"]]
        )
    
    with col2:
        base_conf = st.slider(
            "Base Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.85,
            step=0.05
        )
    
    with col3:
        if st.button("Calculate Adjustment"):
            adjusted_conf, explanation = system.adjust_confidence_score(
                base_confidence=base_conf,
                city=test_city,
                rules_applied=["SAMPLE-RULE"]
            )
            
            st.metric(
                "Adjusted Confidence",
                f"{adjusted_conf:.2%}",
                delta=f"{(adjusted_conf - base_conf)*100:+.1f}%"
            )
            st.info(explanation)
    
    # Close system
    system.close()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Feedback Analytics",
        page_icon="🔄",
        layout="wide"
    )
    render_feedback_analytics()
