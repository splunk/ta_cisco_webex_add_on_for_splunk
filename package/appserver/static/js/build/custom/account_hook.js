class AccountHook {
    /**
     * Form hook
     * @constructor
     * @param {Object} globalConfig - Global configuration.
     * @param {string} serviceName - Service name
     * @param {object} state - Initial state of the form
     * @param {string} mode - Form mode. Can be edit, create or clone
     * @param {object} util - Object containing utility methods
     *                        {
     *                          setState,
     *                          setErrorMsg,
     *                          setErrorFieldMsg,
     *                          clearAllErrorMsg
     *                        }
     */
    constructor (globalConfig, serviceName, state, mode, util) {
        this.globalConfig = globalConfig
        this.serviceName = serviceName
        this.state = state
        this.mode = mode
        this.util = util
    }
  
    /*
      Put logic here to execute javascript on Create UI.
    */
    onCreate () {}
  
    /*
      Put logic here to execute javascript when UI gets rendered.
    */
    onRender () {
        console.log("[-] onRender...")
    }
    /*
      Put form validation logic here.
      Return ture if validation pass, false otherwise.
      Call displayErrorMsg when validtion failed.
    */
    onSave (dataDict) {
        console.log("[-] onSave...")
        console.log("[-] dataDict: ", dataDict);
        const accountName = dataDict.name
        const authType = dataDict.auth_type
        let endpoint = dataDict.endpoint
        console.log("[-] ", accountName, authType, endpoint)
        if (authType === 'oauth') {
            // hard code the scope and state
            const scopeString = "&scope=spark:kms meeting:schedules_read meeting:participants_read&state=set_state_here"
            // append scope string at the end of redirect url
            // to make it send the correct GET request to Webex server with required scopes and state
            const redirect_url = dataDict.redirect_url.concat(scopeString)
            console.log("[-] scopeString ", scopeString)
            console.log("[-] redirect_url ", redirect_url)
            console.log("[-] this.util: ", this.util)
            console.log("[-] this.state: ", this.state)
            this.util.setState((prevState) => {
                const data = { ...prevState.data }
                console.log("[-] data: ", data)
                data.redirect_url.value = redirect_url
                return { data }
            })
        }
        return true
    }
  
    /*
      Put logic here to execute javascript to be called after save success.
    */
    onSaveSuccess () {}
    /*
      Put logic here to execute javascript to be called on save failed.
    */
    onSaveFail () {}
    /*
      Put logic here to execute javascript after loading edit UI.
    */
    onEditLoad () {}
  }
  
  export default AccountHook
