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
            boxCount: this.props.navigation.state.params.boxCount,
            time: new Date()
        }
    }

    static navigationOptions = ({ navigation }) => {
        return {
            title: 'Check In/Out success!',
            headerLeft: (
                <TouchableOpacity><Text style={{
                    fontSize: 50,
                    color: 'white',
                    paddingTop: 5,
                    paddingLeft: 5
                }} onPress={() => navigation.popToTop()} >X</Text></TouchableOpacity>
            ),
        }
    };

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
                <View style={styles.textContainer}>
                    <Text style={styles.text}>
                        Checked {this.props.navigation.state.params.locationData.service.toLowerCase()}
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
