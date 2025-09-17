def get_table_styles():
    """Return the table styling configuration for pandas styler."""
    return [
        {
            'selector': 'th:nth-child(1)',
            'props': [('width', '10%')]
        },
        {
            'selector': 'th:nth-child(2)',
            'props': [('width', '15%')]
        },
        {
            'selector': 'th:nth-child(3)',
            'props': [('width', '25%')]
        },
        {
            'selector': 'th:nth-child(4)',
            'props': [('width', '30%')]
        },
        {
            'selector': 'th:nth-child(5)',
            'props': [('width', '20%')]
        },
        {
            'selector': 'thead th',
            'props': [
                ('background-color', '#667eea'),
                ('color', 'white'),
                ('font-weight', 'bold'),
                ('font-size', '18px'),
                ('padding', '10px 24px'),
                ('text-align', 'center'),
                ('border', 'none')
            ]
        },
        {
            'selector': 'thead th:first-child',
            'props': [
                ('border-top-left-radius', '8px')
            ]
        },
        {
            'selector': 'thead th:last-child',
            'props': [
                ('border-top-right-radius', '8px')
            ]
        },
        {
            'selector': 'tbody td',
            'props': [
                ('font-size', '18px'),
                ('padding', '10px 24px'),
                ('background-color', 'white'),
                ('color', '#2c3e50'),
                ('text-align', 'center'),
                ('font-weight', '400'),
                ('border', 'none')
            ]
        },
        {
            'selector': 'tbody tr:nth-child(even) td',
            'props': [
                ('background-color', '#f8f9fa')
            ]
        },
        {
            'selector': 'tbody tr:hover td',
            'props': [
                ('background-color', '#e3f2fd'),
                ('transition', 'background-color 0.2s ease')
            ]
        },
        {
            'selector': 'table',
            'props': [
                ('border-collapse', 'separate'),
                ('border-spacing', '0'),
                ('width', '100%'),
                ('background-color', 'white'),
                ('border-radius', '8px'),
                ('box-shadow', '0 4px 16px rgba(0,0,0,0.1)'),
                ('overflow', 'hidden'),
                ('margin', '20px 0'),
                ('border', '1px solid #e9ecef')
            ]
        },
        {
            'selector': 'tbody tr',
            'props': [
                ('transition', 'background-color 0.2s ease')
            ]
        }
    ]


def create_scrollable_table(styled_df):
    """Create a scrollable table container with the styled dataframe."""
    # Use render() method for Styler objects
    if hasattr(styled_df, 'render'):
        table_html = styled_df.render()
    else:
        table_html = styled_df.to_html()
    
    scrollable_table = f"""
    <div style="max-height: 400px; overflow-y: auto; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); width: 100%;">
        {table_html}
    </div>
    """
    return scrollable_table
