"""Count likelihoods and fold-local models. Seeds are fixed at 20261002."""
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import gammaln, logsumexp
from scipy.stats import poisson, nbinom
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import PoissonRegressor, Ridge
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor

NUMERIC = ['is_home', 'team_gf', 'team_ga', 'opp_gf', 'opp_ga', 'team_sf',
           'team_sa', 'opp_sf', 'opp_sa', 'team_cf', 'opp_ca', 'rest', 'opp_rest',
           'history_n', 'league_rate']
SEED = 20261002

def poisson_logpmf(y, mean):
    return poisson.logpmf(y, np.maximum(mean, 1e-8))

def nb_logpmf(y, mean, alpha):
    if alpha <= 1e-7:
        return poisson_logpmf(y, mean)
    size = 1 / alpha
    return nbinom.logpmf(y, size, size / (size + mean))

def bivariate_logpmf(h, a, mh, ma, rho):
    """Shared count c = rho * min(mh, ma); preserves specified marginal means."""
    if rho <= 1e-8:
        return poisson_logpmf(h, mh) + poisson_logpmf(a, ma)
    h, a, mh, ma = np.broadcast_arrays(h, a, mh, ma)
    shared = np.maximum(rho * np.minimum(mh, ma), 1e-12)
    lh, la = np.maximum(mh-shared, 1e-12), np.maximum(ma-shared, 1e-12)
    max_k = int(np.minimum(h, a).max())
    terms = []
    for k in range(max_k + 1):
        terms.append(np.where((k <= h) & (k <= a),
            poisson.logpmf(h-k, lh)+poisson.logpmf(a-k, la)+poisson.logpmf(k, shared), -np.inf))
    return logsumexp(np.array(terms), axis=0)

class NBRegressor:
    """NB2 log-link regression with training-only standardized features."""
    def __init__(self, penalty=0.1):
        self.penalty = penalty
    def fit(self, x, y):
        self.scaler = StandardScaler().fit(x)
        z = np.column_stack([np.ones(len(x)), self.scaler.transform(x)])
        y = np.asarray(y)
        def objective(theta):
            mu = np.exp(np.clip(z @ theta[:-1], -12, 12))
            alpha = np.exp(theta[-1])
            return -nb_logpmf(y, mu, alpha).mean() + self.penalty * np.sum(theta[1:-1]**2)/2
        initial = np.zeros(z.shape[1]+1)
        initial[0] = np.log(y.mean())
        initial[-1] = np.log(.05)
        bounds = [(None, None)] * z.shape[1] + [(-14, 2)]
        fit = minimize(objective, initial, method='L-BFGS-B', bounds=bounds,
                       options={'maxiter': 1000, 'ftol': 1e-10})
        if not fit.success:
            raise RuntimeError(f'NB optimizer failed: {fit.message}')
        self.beta, self.alpha = fit.x[:-1], float(np.exp(fit.x[-1]))
        self.optimization_message = str(fit.message)
        return self
    def predict(self, x):
        z = np.column_stack([np.ones(len(x)), self.scaler.transform(x)])
        return np.exp(np.clip(z @ self.beta, -12, 12))

def fit_model(name, train, config):
    y = train.target.to_numpy()
    if name == 'negative_binomial':
        return NBRegressor(config['alpha']).fit(train[NUMERIC], y)
    if name == 'attack_defence_poisson':
        transformer = ColumnTransformer([
            ('numeric', StandardScaler(), ['is_home', 'league_rate']),
            ('teams', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['team','opponent'])])
    else:
        transformer = ColumnTransformer([('numeric', StandardScaler(), NUMERIC)])
    if name in ['poisson', 'attack_defence_poisson', 'bivariate_poisson']:
        estimator = PoissonRegressor(alpha=config['alpha'], max_iter=1000, tol=1e-8)
    elif name == 'ridge_poisson_proxy':
        estimator = Ridge(alpha=config['alpha'])
    elif name == 'boosted_poisson':
        estimator = HistGradientBoostingRegressor(loss='poisson', max_iter=config['iterations'],
            max_leaf_nodes=config['leaves'], min_samples_leaf=50, l2_regularization=1.,
            learning_rate=.05, early_stopping=False, random_state=SEED)
    elif name == 'random_forest_poisson_proxy':
        estimator = RandomForestRegressor(n_estimators=250, min_samples_leaf=config['leaf'],
            max_features=.8, n_jobs=4, random_state=SEED)
    else:
        raise ValueError(name)
    return Pipeline([('prep', transformer), ('model', estimator)]).fit(train, y)

def predict_model(name, fitted, stacked):
    x = stacked[NUMERIC] if name == 'negative_binomial' else stacked
    return np.maximum(fitted.predict(x), .05)

def marginal_quantiles(mean, alpha=0):
    if alpha <= 1e-7:
        return poisson.ppf(.05, mean), poisson.ppf(.95, mean)
    size = 1/alpha
    return nbinom.ppf(.05, size, size/(size+mean)), nbinom.ppf(.95, size, size/(size+mean))

def outcome_probabilities(mh, ma, alpha=0, rho=0, cap=35):
    # Finite-grid approximation checked for negligible missing mass.
    grid = np.arange(cap+1)
    output = []
    for h, a in zip(mh, ma):
        if rho > 0:
            joint = np.exp(bivariate_logpmf(grid[:,None], grid[None,:], h, a, rho))
        else:
            ph = np.exp(nb_logpmf(grid, h, alpha))
            pa = np.exp(nb_logpmf(grid, a, alpha))
            joint = np.outer(ph, pa)
        mass = joint.sum()
        if mass < 1-1e-7:
            raise ValueError('Score grid truncates material probability mass')
        output.append([np.tril(joint,-1).sum()/mass, np.trace(joint)/mass, np.triu(joint,1).sum()/mass])
    return np.asarray(output)
