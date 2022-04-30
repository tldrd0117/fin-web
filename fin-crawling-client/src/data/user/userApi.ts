

const url = process.env.NODE_ENV=="production"?"/user/":"http://localhost:30005/user/"

const BASEURL = url;

const commonHeader = {
    "Content-Type": "application/json",
    "Authorization": "application/json",

}

export const getPublicKey = async () => {
    try{
        console.log("getPublicKey")
        const response: Response = await fetch(`${BASEURL}publicKey`, {
            method: "POST",
            body: ""
        })
        const json = await response.json()
        return {response: json}
    } catch(e) {
        console.log(e)
        return {error: e};
    }
}


export const getToken = async (username: string, password: string) => {
    const formData = new FormData()
    formData.append("username", username);
    formData.append("password", password);
    console.log("getToken: " + username)
    try{
        const response: Response = await fetch(`${BASEURL}token`,{
            method: "POST",
            body: formData
        })
        const json = await response.json()
        return {response: json}
    } catch(e){
        console.log(e)
        return {error: e};
    }
}

export const join = async (username: string, hashedPassword: string, email: string, salt: string) => {
    // const formData = new FormData()
    // formData.append("username", username);
    // formData.append("password", password);
    // formData.append("email", email);
    try{
        const response: Response = await fetch(`${BASEURL}join`, {
            method: "POST",
            body: JSON.stringify({
                username, hashedPassword, email, salt
            })
        })
        const json = await response.json()
        return {response: json}
    } catch(e) {
        console.log(e)
        return {error: e};
    }
}

export const getMe = async (token: string) => {
    console.log("getMe")
    const response: Response = await fetch(`${BASEURL}me`,{
        body: JSON.stringify({
            token
        })
    })
    return await response.json()
}
