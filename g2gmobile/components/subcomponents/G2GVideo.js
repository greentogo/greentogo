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
// import Video from 'react-native-video';
// import VideoPlayer from 'react-native-video-controls';
import { Video } from 'expo';
import VideoPlayer from '@expo/videoplayer';


import { MaterialIcons, Octicons } from '@expo/vector-icons';


class G2GVideo extends React.Component {
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

    render() {
        const win = Dimensions.get('window');
        return (
            <View>
                <VideoPlayer
                    videoProps={{
                        resizeMode:"cover",
                        shouldPlay: this.state.shouldPlay,
                        isMuted: this.state.mute,
                        // style:{
                        //     alignSelf: 'stretch',
                        //     width: win.width,
                        //     height: win.width / 2
                        // },
                        ignoreSilentSwitch:"ignore",
                        source: {
                            uri: '../../assets/icons/how-2-gtg.mp4'
                        }
                    }}
                    showControlsOnLoad={true}
                    isPortrait={true}
                />
                <Video
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
                />
                <View style={{
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: 45,
                    flexDirection: 'row',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: "rgba(0, 0, 0, 0.5)",
                }}>
                    <MaterialIcons
                        name={this.state.mute ? "volume-mute" : "volume-up"}
                        size={45}
                        color="white"
                        onPress={this.handleVolume}
                    />
                    <MaterialIcons
                        name={this.state.shouldPlay ? "pause" : "play-arrow"}
                        size={45}
                        color="white"
                        onPress={this.handlePlayAndPause}
                    />
                </View>
            </View>
        )
    }
}

export default G2GVideo;
