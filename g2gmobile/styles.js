import { StyleSheet, Dimensions } from 'react-native';
import { Constants } from 'expo';

const primaryColor = '#628E86';
// const primaryCream = '#F8F8F4';
const primaryCream = '#f9f9e8';
// const primaryCream = 'rgb(248, 248, 244)';

const styles = {
    primaryColor: primaryColor,
    primaryCream: primaryCream,
    creamBackground: {
        backgroundColor: primaryCream
    },
    container: {
        flex: 1,
        backgroundColor: primaryCream 
    },
    popToTopStyle: {
        fontSize: 40,
        color: 'white',
        paddingTop: 5,
        paddingLeft: 5
    },
    centeredRow: {
        flexDirection: 'row',
        justifyContent: 'center',
        marginTop: 5,
        marginBottom: 5
    },
    pickerStyle: {
        borderWidth: 1,
        borderColor: '#000000'
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center'
    },
    errorStyle: {
        color: 'red',
        textAlign: 'center'
    },
    boldCenteredText: {
        paddingTop: 5,
        paddingBottom: 5,
        color: primaryColor,
        fontWeight: '800',
        fontSize: 20,
        textAlign: 'center'
    },
    submissionContainer: {
        flex: 1,
        backgroundColor: primaryCream,
        flexDirection: 'column',
        justifyContent: 'space-around',
    },
    submissionAddSubIcon: {
        fontSize: 30,
        fontWeight: '800',
        color: 'white',
        textAlign: 'center',
        width: 50,
        alignSelf: 'center'
    },
    submissionBoxCountStyle: {
        marginLeft: 10,
        marginRight: 10,
        fontSize: 30,
        alignSelf: 'center'
    },
    submissionSubmitButton: {
        paddingRight: 20,
        paddingLeft: 20,
        paddingTop: 20,
        paddingBottom: 20,
        backgroundColor: '#5fb75f',
        borderRadius: 10
        // borderWidth: 1,
        // borderColor: '#fff'
    },
    submissionSubmitButtonBlocked: {
        paddingRight: 20,
        paddingLeft: 20,
        paddingTop: 20,
        paddingBottom: 20,
        backgroundColor: '#808080',
        borderRadius: 10
        // borderWidth: 1,
        // borderColor: '#fff'
    },
    submissionSubmitTextStyle: {
        fontSize: 30,
        color: 'white'
    },
    successTopContainer: {
        backgroundColor: primaryColor,
        flex: 1,
        flexDirection: 'column',
    },
    successText: {
        color: 'white',
        textAlign: 'center',
        fontSize: 45
    },
    successDateTimeText: {
        color: 'white',
        textAlign: 'center',
        fontSize: 30
    },
    successImageContainer: {
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 50
    },
    successImage: {
        height: 140,
        width: 140
    },
    window: {
       height: Dimensions.get('window').height,
       width: Dimensions.get('window').width
    }
}

// const stylesheet = StyleSheet.create(styles)

export default styles;
