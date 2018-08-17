def slider_stylesheet(*, handle_color = '#ed3232', groove_color_start = '#000000', 
    groove_color_stop = '#FFFFFF'):
    return f"""
            QSlider::groove:vertical {{
                border: 1px solid #999999;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {groove_color_stop}, stop:1 {groove_color_start});
                margin: 5px 0;
                width: 8
            }}
            QSlider::handle:vertical {{
                background: {handle_color};
                border: 10px solid {handle_color};
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 10px;
            }}
        """

def main_window(*, bg = '#424242'):
    return f"""
        background-color: {bg};
    """