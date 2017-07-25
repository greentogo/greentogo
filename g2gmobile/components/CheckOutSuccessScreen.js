import React from 'react';
import {
    StyleSheet,
    Text,
    View,
    Image,
    TouchableOpacity
} from 'react-native';

class CheckOutSuccessScreen extends React.Component {
   constructor(props) {
        super(props)
        this.state = {
            boxCount: this.props.route.params.boxCount,
            time: new Date()
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
              paddingTop: 18,
              backgroundColor: '#ffffff'
            },
            goHomeButton: {
              fontSize: 50,
              color: 'white',
              paddingTop: 5,
              paddingLeft: 5
            },
            checkOutTextContainer: {
                flex: 1,
                flexDirection: 'column',
                justifyContent: 'center'
            },
            checkOutText: {
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
            <View style={styles.statusBar}></View>
                <TouchableOpacity>
                    <Text
                      style={styles.goHomeButton}
                      onPress={() => this.goHome()}
                    >X</Text>
                </TouchableOpacity>
                <View style={styles.checkOutTextContainer}>
                    <Text style={styles.checkOutText}>
                        Checked out
                    </Text>
                    <Text style={styles.checkOutText}>
                        {this.state.boxCount === 1 ? "1 box" : this.state.boxCount + " boxes"}
                    </Text>
                    {/* TODO: Give location name on successful checkOut and set it to state */
                    }
                    {/* <Text style={{color: 'white', textAlign: 'center', fontSize: 45}}>
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
                            style={{ height: 140, width: 140}}
                        />
                    </View>
                </View>
            </View>
        )
    }
}

export default CheckOutSuccessScreen;
