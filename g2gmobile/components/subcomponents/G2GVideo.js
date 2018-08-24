import React from 'react';
import {
    StyleSheet,
    View,
    TouchableHighlight,
    ScrollView,
    Dimensions
} from 'react-native';
import styles from "../../styles";
import {
    Content,
    List,
    Text
} from "native-base";
import { Video } from 'expo';
import VideoPlayer from './VideoPlayer';
import BaseScreen from './BaseScreen';


class G2GVideo extends BaseScreen {
    constructor(props) {
        super(props)
        this.state = {
            mute: false,
            shouldPlay: false,
        }
    }

    handlePlayAndPause = () => {
        this.setState(prevState => ({
            shouldPlay: !prevState.shouldPlay
        }));
    }

    handleVolume = () => {
        this.setState(prevState => ({
            mute: !prevState.mute,
        }));
    }


    changeRate(rate) {
        this._playbackInstance.setStatusAsync({
            rate: rate,
            shouldCorrectPitch: true,
        });
    }

    render() {
        const win = Dimensions.get('window');
        return (
            <View>
                <VideoPlayer
                    videoProps={{
                        shouldPlay: false,
                        resizeMode: Video.RESIZE_MODE_CONTAIN,
                        isMuted: false,
                        ref: component => {
                            this._playbackInstance = component;
                        },
                    }}
                    showControlsOnLoad={true}
                    isPortrait={this.state.isPortrait}
                    switchToLandscape={this.switchToLandscape.bind(this)}
                    switchToPortrait={this.switchToPortrait.bind(this)}
                    playFromPositionMillis={0}
                />
                {/* <Video
                    resizeMode="cover"
                    shouldPlay={this.state.shouldPlay}
                    isMuted={this.state.mute}
                    style={{
                        alignSelf: 'stretch',
                        width: win.width,
                        height: win.width / 2
                    }}
                    ignoreSilentSwitch="ignore"
                    source={require('../../assets/icons/how-2-gtg.mp4')}
                /> */}
            </View>
        )
    }
}

export default G2GVideo;
