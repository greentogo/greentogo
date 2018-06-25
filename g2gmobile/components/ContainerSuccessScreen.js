import React from 'react';
import {
    StyleSheet,
    Text,
    View,
    Image,
    TouchableOpacity
} from 'react-native';
import { Constants } from 'expo';

class ContainerSuccessScreen extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            boxCount: this.props.route.params.boxCount,
            time: new Date()
        }
    }
    static route  = {
        navigationBar: {
            title: `Check In/Out success!`,
            renderLeft: (route, props) => null
        }
    }

    goHome = () => {
        this.props.navigator.popToTop();
    }

    render() {
        const styles = StyleSheet.create({
            topContainer: {
                backgroundColor: '#628E86',
                flex: 1,
                flexDirection: 'column'
            },
            statusBar: {
                paddingTop: Constants.statusBarHeight,
                backgroundColor: '#ffffff'
            },
            goHomeButton: {
                fontSize: 50,
                color: 'white',
                paddingTop: 5,
                paddingLeft: 5
            },
            textContainer: {
                flex: 1,
                flexDirection: 'column',
                //alignItems: 'center',//????
                justifyContent: 'center'
            },
            text: {
                color: 'white',
                textAlign: 'center',
                fontSize: 45
            },
            dateTimeText: {
                color: 'white',
                textAlign: 'center',
                fontSize: 30
            },
            imageContainer: {
                justifyContent: 'center',
                alignItems: 'center',
                marginTop: 50
            }
        });

        return (
            <View style={styles.topContainer}>
                <TouchableOpacity>
                    <Text
                        style={styles.goHomeButton}
                        onPress={() => this.goHome()}
                    >X</Text>
                </TouchableOpacity>
                <View style={styles.textContainer}>
                    <Text style={styles.text}>
                        Checked out
                    </Text>
                    <Text style={styles.text}>
                        {this.state.boxCount === 1 ? "1 box" : this.state.boxCount + " boxes"}
                    </Text>
                    {/* TODO: Give location name on successful checkOut and set it to state */
                    }
                    {/* <Text style={{color: '#628e86', textAlign: 'center', fontSize: 45}}>
                    {this.state.location ? "from " + this.state.location : ""}
                    </Text> */}
                    <Text style={styles.dateTimeText}>
                        {this.state.time ? this.state.time.toLocaleTimeString() : ""}
                    </Text>
                    <Text style={styles.dateTimeText}>
                        {this.state.time ? this.state.time.toLocaleDateString() : ""}
                    </Text>
                    <View style={styles.imageContainer}>
                        <Image
                            source={require('../assets/icons/GTG-Box-App.png')}
                            style={{ height: 140, width: 140 }}
                        />
                    </View>
                </View>
            </View>
        )
    }
}

export default ContainerSuccessScreen;
