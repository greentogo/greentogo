import { StyleSheet } from 'react-native';
import { Constants } from 'expo';

const styles = {
    buttonContainer: {
        padding: 10,
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
    },
    container: {
        flex: 1,
        backgroundColor: '#fff',
        justifyContent: 'center',
        paddingTop: Constants.statusBarHeight,
    },
    fullWidthButton: {
        width: '100%',
        justifyContent: 'center',
        flex: 1,
    },
    boldText: {
        fontWeight: 'bold'
    },
    bigText: {
        fontSize: 30
    }
}

// const stylesheet = StyleSheet.create(styles)

export default styles;
