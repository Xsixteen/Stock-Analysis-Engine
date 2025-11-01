#!/usr/bin/env python3
"""
Screener Pipeline Step 04: Generate Markdown Report
Converts gpt_analysis.json into a readable markdown report with summary tables
"""
import json
from datetime import datetime

def load_gpt_analysis():
    """Load GPT analysis data from gpt_analysis.json"""
    with open("data/gpt_analysis.json", "r") as f:
        return json.load(f)

def format_list_items(items, indent=0):
    """Format a list of items as markdown bullet points"""
    indent_str = "  " * indent
    return "\n".join([f"{indent_str}- {item}" for item in items])

def get_emoji_for_rating(rating):
    """Get an emoji based on the rating"""
    if rating >= 8:
        return "🟢"
    elif rating >= 6:
        return "🟡"
    else:
        return "🔴"

def get_emoji_for_signal(signal):
    """Get an emoji based on the buy signal"""
    signal_map = {
        "strong_buy": "🚀",
        "buy": "✅",
        "hold": "⏸️",
        "sell": "⬇️",
        "strong_sell": "🛑"
    }
    return signal_map.get(signal.lower(), "❓")

def generate_summary_table(analyses):
    """Generate a summary table of all stocks"""
    lines = [
        "| Ticker | Rating | Valuation | Signal | Entry Quality |",
        "|--------|--------|-----------|--------|---------------|"
    ]

    for ticker, analysis in analyses.items():
        if "error" in analysis:
            lines.append(f"| {ticker} | ❌ Error | - | - | - |")
        else:
            rating = analysis.get('rating', 'N/A')
            rating_emoji = get_emoji_for_rating(rating) if isinstance(rating, (int, float)) else ""
            valuation = analysis.get('valuation', 'N/A').replace('_', ' ').title()
            signal = analysis.get('buy_signal', 'N/A').replace('_', ' ').title()
            signal_emoji = get_emoji_for_signal(analysis.get('buy_signal', ''))
            entry = analysis.get('entry_point_quality', 'N/A').title()

            lines.append(f"| {ticker} | {rating_emoji} {rating}/10 | {valuation} | {signal_emoji} {signal} | {entry} |")

    return "\n".join(lines)

def generate_detailed_analysis(ticker, analysis):
    """Generate detailed markdown for a single stock"""
    if "error" in analysis:
        return f"### {ticker}\n\n**Error:** {analysis['error']}\n"

    rating = analysis.get('rating', 'N/A')
    rating_emoji = get_emoji_for_rating(rating) if isinstance(rating, (int, float)) else ""
    valuation = analysis.get('valuation', 'N/A').replace('_', ' ').title()
    signal = analysis.get('buy_signal', 'N/A').replace('_', ' ').title()
    signal_emoji = get_emoji_for_signal(analysis.get('buy_signal', ''))
    entry = analysis.get('entry_point_quality', 'N/A').title()

    sections = [
        f"### {ticker}",
        "",
        f"**Rating:** {rating_emoji} {rating}/10",
        f"**Valuation:** {valuation}",
        f"**Buy Signal:** {signal_emoji} {signal}",
        f"**Entry Point Quality:** {entry}",
        "",
        "#### Summary",
        analysis.get('summary', 'No summary available.'),
        "",
        "#### Technical Analysis",
        analysis.get('technical_summary', 'No technical summary available.'),
        "",
        "#### Strengths",
        format_list_items(analysis.get('strengths', ['No strengths listed'])),
        "",
        "#### Weaknesses",
        format_list_items(analysis.get('weaknesses', ['No weaknesses listed'])),
        ""
    ]

    return "\n".join(sections)

def generate_markdown_report(data):
    """Generate complete markdown report"""
    timestamp = data.get('timestamp', 'Unknown')
    model = data.get('model', 'Unknown')
    count = data.get('count', 0)
    analyses = data.get('analyses', {})

    # Parse timestamp for better formatting
    try:
        dt = datetime.fromisoformat(timestamp)
        formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        formatted_time = timestamp

    # Calculate some quick stats
    successful = sum(1 for v in analyses.values() if "error" not in v)
    strong_buys = sum(1 for v in analyses.values() if v.get('buy_signal') == 'strong_buy')
    buys = sum(1 for v in analyses.values() if v.get('buy_signal') == 'buy')

    # Build markdown document
    sections = [
        "# Stock Screener Analysis Report",
        "",
        f"**Generated:** {formatted_time}",
        f"**AI Model:** {model}",
        f"**Stocks Analyzed:** {successful}/{count}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **Strong Buy Signals:** {strong_buys}",
        f"- **Buy Signals:** {buys}",
        f"- **Total Opportunities:** {strong_buys + buys}",
        "",
        "## Summary Table",
        "",
        generate_summary_table(analyses),
        "",
        "---",
        "",
        "## Detailed Analysis",
        ""
    ]

    # Add detailed analysis for each stock
    for ticker in sorted(analyses.keys()):
        sections.append(generate_detailed_analysis(ticker, analyses[ticker]))
        sections.append("---")
        sections.append("")

    # Add legend at the end
    sections.extend([
        "## Legend",
        "",
        "**Ratings:**",
        "- 🟢 8-10: High quality stock",
        "- 🟡 6-7: Medium quality stock",
        "- 🔴 1-5: Low quality stock",
        "",
        "**Buy Signals:**",
        "- 🚀 Strong Buy",
        "- ✅ Buy",
        "- ⏸️ Hold",
        "- ⬇️ Sell",
        "- 🛑 Strong Sell",
        "",
        "**Valuation:**",
        "- Undervalued: Stock is trading below its intrinsic value",
        "- Fairly Valued: Stock is trading at approximately its intrinsic value",
        "- Overvalued: Stock is trading above its intrinsic value",
        "",
        "**Entry Point Quality:**",
        "- Excellent: Very favorable time to enter position",
        "- Good: Favorable time to enter position",
        "- Fair: Acceptable time to enter position",
        "- Poor: Unfavorable time to enter position",
        ""
    ])

    return "\n".join(sections)

def main():
    print("="*60)
    print("SCREENER STEP 04: Generate Markdown Report")
    print("="*60)

    try:
        # Load GPT analysis data
        print("\n📊 Loading analysis data...")
        data = load_gpt_analysis()

        # Generate markdown report
        print("📝 Generating markdown report...")
        markdown_content = generate_markdown_report(data)

        # Save to file
        output_path = "data/screener_report.md"
        with open(output_path, "w") as f:
            f.write(markdown_content)

        print(f"\n✓ Report generated successfully")
        print(f"  Saved to: {output_path}")
        print(f"  Stocks analyzed: {data.get('count', 0)}")
        print("\nStep 04 complete")

    except FileNotFoundError:
        print("\n❌ FAILED: gpt_analysis.json not found")
        print("   Please run step 03 (GPT analysis) first")
        exit(1)
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        exit(1)

if __name__ == "__main__":
    main()
