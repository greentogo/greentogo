import React from 'react';
import { Animated } from 'react-native';

class Flashing extends React.Component {
    state = {
        fadeAnim: new Animated.Value(0),  // Initial value for opacity: 0
    }

    componentDidMount() {
        this.cycleAnimation();
    }

    cycleAnimation() {
        Animated.sequence([
            Animated.timing(this.state.fadeAnim, { // Animate over time
                toValue: 1,                 // Animate to opacity: 1 (opaque)
                duration: 500              // Make it take a while
            }),
            Animated.timing(this.state.fadeAnim, {  // The animated value to drive
                toValue: 0,
                duration: 500,
                delay: 500                // Make it last for a little
            })
        ]).start(() => {                // Starts the animation
            this.cycleAnimation();
        });
    }

    render() {
        let { fadeAnim } = this.state;
        return (
            <Animated.View                 // Special animatable View
                style={{
                    ...this.props.style,
                    opacity: fadeAnim,         // Bind opacity to animated value
                }}
            >
                {this.props.children}
            </Animated.View>
        );
    }
}

export default Flashing;
