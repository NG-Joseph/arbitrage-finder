import betWay from '@betting-api/betway'

betWay.registerApp({
    secret_key: '31317d10125a4b41a1e9ee76e80ab3470a575a27fb6b416a8be61296ad0f2b39',
})

const getList = async () => {
    
    const prematchList = await betWay.football.getPreMatchAll()

    return prematchList


}

getList()

